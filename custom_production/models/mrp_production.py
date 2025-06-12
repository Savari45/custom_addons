from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    is_initial_produced = fields.Boolean("Initial Produced", default=False)
    is_validated = fields.Boolean("Components Validated", default=False)

    def action_initial_produce(self):
        """
        This just flags the order as having started initial production.
        Does not consume materials or mark done quantities.
        """
        for order in self:
            if order.is_initial_produced:
                raise UserError("Initial production has already been done.")
            if order.state not in ['confirmed', 'progress', 'to_close']:
                raise UserError("Manufacturing order must be confirmed or in progress.")

            order.is_initial_produced = True
            order.state = 'progress'  # Move to progress state to allow component changes

    def action_validate_components(self):
        """
        Once components are checked/modified and finalized.
        """
        for order in self:
            if not order.is_initial_produced:
                raise UserError("You must perform initial production first.")
            order.is_validated = True

    def action_reproduce(self):
        """
        Final production action that consumes component quantities and marks finished goods as done.
        """
        for order in self:
            if not order.is_validated:
                raise UserError("You must validate components before final production.")

            # Consume raw materials
            for move in order.move_raw_ids.filtered(lambda m: m.state not in ('done', 'cancel')):
                for line in move.move_line_ids.filtered(lambda l: l.state not in ('done', 'cancel')):
                    line.qty_done = move.product_uom_qty
                move._action_done()

            # Produce finished goods
            for move in order.move_finished_ids.filtered(lambda m: m.state not in ('done', 'cancel')):
                for line in move.move_line_ids.filtered(lambda l: l.state not in ('done', 'cancel')):
                    line.qty_done = move.product_uom_qty
                move._action_done()

            order.state = 'done'

    def action_change_components(self):
        """
        Allow modification of raw materials after initial production but before validation.
        """
        for order in self:
            if not order.is_initial_produced:
                raise UserError("Initial production must be done before you can change components.")
            if order.state == 'done':
                raise UserError("Cannot change components after production is completed.")
            if order.is_validated:
                raise UserError("Cannot change components after validation.")

            # Allow manual modifications in the UI — no code changes here
            # Just allow editing/deleting raw material lines

            # Optionally: You can log that component change was triggered
            _logger.info("Component change action opened for MO %s", order.name)

    @api.model
    def create(self, vals):
        vals.setdefault('state', 'draft')
        return super(MrpProduction, self).create(vals)


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.ondelete(at_uninstall=False)
    def _unlink_if_draft_or_cancel(self):
        for move in self:
            production = move.raw_material_production_id or move.production_id
            if production:
                if production.is_initial_produced and not production.is_validated:
                    continue  # Allow deletion before validation

            if move.state not in ('draft', 'cancel') and (move.move_orig_ids or move.move_dest_ids):
                raise UserError(_('You cannot delete moves linked to another operation.'))
