from odoo import models, fields, api

class ProductProduct(models.Model):
    _inherit = 'product.product'

    available_qty_in_pos = fields.Float(
        string="POS Available Quantity",
        compute='_compute_available_qty_in_pos',
        store=False
    )

    available_in_pos = fields.Boolean(
        string="Available in POS",
        compute='_compute_available_in_pos',
        store=False
          # ✅ Must be stored to avoid search error
    )

    @api.depends_context('uid')
    def _compute_available_qty_in_pos(self):
        user = self.env.user
        warehouse = user.property_warehouse_id

        stock_locations = self.env['stock.location'].search([
            ('id', 'child_of', warehouse.lot_stock_id.id),
            ('usage', '=', 'internal'),
        ]) if warehouse else []

        quant_data = self.env['stock.quant'].sudo().read_group(
            [('location_id', 'in', stock_locations.ids)],
            ['product_id', 'quantity'],
            ['product_id']
        ) if stock_locations else []

        qty_map = {q['product_id'][0]: q['quantity'] for q in quant_data}

        for product in self:
            product.available_qty_in_pos = qty_map.get(product.id, 0.0)

    @api.depends_context('uid')
    def _compute_available_in_pos(self):
        self._compute_available_qty_in_pos()
        for product in self:
            product.available_in_pos = product.available_qty_in_pos > 0.0
