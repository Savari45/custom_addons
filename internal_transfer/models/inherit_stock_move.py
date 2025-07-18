from odoo import models, fields, api

class StockMove(models.Model):
    _inherit = 'stock.move'

    cost_price = fields.Float(
        string='Cost Price',
        compute='_compute_transfer_cost',  # ✅ Correct method name
        store=True,
        readonly=True
    )
    transfer_cost = fields.Float(
        string='Total Cost',
        compute='_compute_transfer_cost',  # ✅ Correct method name
        store=True,
        readonly=True
    )
    display_name = fields.Char(compute='_compute_display_name', store=True, string="On Hand")

    @api.depends('product_id', 'location_id')
    def _compute_display_name(self):
        for move in self:
            name = move.product_id.display_name or ''
            qty = 0
            if move.product_id and move.location_id:
                qty = self.env['stock.quant']._get_available_quantity(move.product_id, move.location_id)
            move.display_name = f"{int(qty)}"

    @api.depends('product_id', 'product_uom_qty')
    def _compute_transfer_cost(self):
        for move in self:
            cost = move.product_id.standard_price or 0.0
            move.cost_price = cost
            move.transfer_cost = cost * move.product_uom_qty

