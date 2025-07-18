from odoo import models, fields, api, _
from odoo.tools.float_utils import float_is_zero
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    branch_company_id = fields.Many2one(
        'res.company',
        string="Destination Branch Company",
        domain=lambda self: [('id', '!=', self.env.company.id)],
        help="Select the destination branch company for automatic internal transfer creation."
    )

    total_transfer_cost = fields.Float(
        string='Total Transfer Cost',
        compute='_compute_total_transfer_cost',
        store=True
    )

    @api.depends('move_ids.transfer_cost')
    def _compute_total_transfer_cost(self):
        for picking in self:
            picking.total_transfer_cost = sum(picking.move_ids.mapped('transfer_cost'))

    def button_validate(self):
        # Confirm and assign stock for draft pickings
        draft_pickings = self.filtered(lambda p: p.state == 'draft')
        draft_pickings.action_confirm()


        for move in draft_pickings.move_ids:
            if float_is_zero(move.quantity, precision_rounding=move.product_uom.rounding) and \
                    not float_is_zero(move.product_uom_qty, precision_rounding=move.product_uom.rounding):
                move.quantity = move.product_uom_qty

        if not self.env.context.get('skip_sanity_check', False):
            self._sanity_check()

        self.message_subscribe([self.env.user.partner_id.id])

        if not self.env.context.get('button_validate_picking_ids'):
            self = self.with_context(button_validate_picking_ids=self.ids)

        res = self._pre_action_done_hook()
        if res is not True:
            return res

        # Handle backorders
        no_backorder = self.filtered(lambda p: p.picking_type_id.create_backorder == 'never')
        if self.env.context.get('picking_ids_not_to_backorder'):
            no_backorder |= self.browse(self.env.context['picking_ids_not_to_backorder']).filtered(
                lambda p: p.picking_type_id.create_backorder != 'always'
            )
        to_backorder = self - no_backorder
        no_backorder.with_context(cancel_backorder=True)._action_done()
        to_backorder.with_context(cancel_backorder=False)._action_done()

        # Create inter-company internal transfers
        for picking in self:
            if picking.picking_type_id.code != 'internal':
                continue
            if picking.location_dest_id.usage != 'transit' or 'inter' not in picking.location_dest_id.name.lower():
                continue

            dest_company = picking.branch_company_id
            if not dest_company:
                raise ValidationError(_("Please select a destination branch company for this inter-company transfer."))

            branch_wh = self.env['stock.warehouse'].sudo().search([
                ('company_id', '=', dest_company.id)
            ], limit=1)
            if not branch_wh:
                raise ValidationError(_("No warehouse found for destination company %s.") % dest_company.name)

            picking_type = self.env['stock.picking.type'].sudo().search([
                ('code', '=', 'internal'),
                ('company_id', '=', dest_company.id)
            ], limit=1)

            if not picking_type:
                picking_type = self.env['stock.picking.type'].sudo().create({
                    'name': 'Internal Transfer',
                    'code': 'internal',
                    'company_id': dest_company.id,
                    'sequence_code': 'INT',
                    'warehouse_id': branch_wh.id,
                    'default_location_src_id': branch_wh.lot_stock_id.id,
                    'default_location_dest_id': branch_wh.lot_stock_id.id,
                })

            new_picking = self.env['stock.picking'].sudo().create({
                'picking_type_id': picking_type.id,
                'location_id': picking.location_dest_id.id,
                'location_dest_id': branch_wh.lot_stock_id.id,
                'company_id': dest_company.id,
                'origin': _('Auto created from %s') % picking.name,
            })

            for move in picking.move_ids:
                self.env['stock.move'].sudo().create({
                    'picking_id': new_picking.id,
                    'product_id': move.product_id.id,
                    'product_uom_qty': move.product_uom_qty,
                    'product_uom': move.product_uom.id,
                    'name': move.name,
                    'location_id': picking.location_dest_id.id,
                    'location_dest_id': branch_wh.lot_stock_id.id,
                    'company_id': dest_company.id,
                })

                if not float_is_zero(move.product_uom_qty, precision_rounding=move.product_uom.rounding):
                    dest_product = move.product_id.with_company(dest_company)
                    dest_product.standard_price = move.product_id.standard_price

            # Confirm & reserve inter-company picking (inside loop)
            new_picking.action_confirm()
            new_picking.action_assign()

            picking.message_post(body=_(
                "✅ Inter-company draft transfer created in <b>%s</b>: %s"
            ) % (dest_company.name, new_picking.name))

        # Handle auto-printing reports
        report_actions = self._get_autoprint_report_actions()
        another_action = False

        if self.env.user.has_group('stock.group_reception_report'):
            to_report = self.filtered(lambda p: p.picking_type_id.auto_show_reception_report)
            lines = to_report.move_ids.filtered(
                lambda m: m.product_id.is_storable and m.state != 'cancel' and m.quantity and not m.move_dest_ids
            )
            if lines:
                view_locs = self.env['stock.location']._search([
                    ('id', 'child_of', to_report.picking_type_id.warehouse_id.view_location_id.ids),
                    ('usage', '!=', 'supplier')
                ])
                move_exists = self.env['stock.move'].search_count([
                    ('state', 'in', ['confirmed', 'partially_available', 'waiting', 'assigned']),
                    ('product_qty', '>', 0),
                    ('location_id', 'in', view_locs),
                    ('move_orig_ids', '=', False),
                    ('picking_id', 'not in', to_report.ids),
                    ('product_id', 'in', lines.product_id.ids)
                ], limit=1)
                if move_exists:
                    action = to_report.action_view_reception_report()
                    action['context'] = {'default_picking_ids': to_report.ids}
                    if not report_actions:
                        return action
                    another_action = action

        if report_actions:
            return {
                'type': 'ir.actions.client',
                'tag': 'do_multi_print',
                'params': {
                    'reports': report_actions,
                    'anotherAction': another_action,
                }
            }

        return True
