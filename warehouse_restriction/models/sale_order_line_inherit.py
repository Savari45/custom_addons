from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    allowed_product_ids = fields.Many2many(
        'product.template',
        compute='_compute_allowed_product_templates',
        store=False,
        string='Allowed Products'
    )

    def _get_available_product_and_template_ids(self):
        product_ids = []
        template_ids = []

        order = self.order_id
        partner = order.partner_id
        warehouse = order.warehouse_id

        if not partner or not warehouse:
            # Don't return anything if customer or warehouse not selected
            return product_ids, template_ids

        # Get internal stock locations under the warehouse
        stock_locations = self.env['stock.location'].search([
            ('id', 'child_of', warehouse.lot_stock_id.id),
            ('usage', '=', 'internal')
        ])

        if stock_locations:
            self.env.cr.execute("""
                SELECT DISTINCT product_id
                FROM stock_quant
                WHERE location_id IN %s AND quantity > 0
            """, (tuple(stock_locations.ids),))
            product_ids = [row[0] for row in self.env.cr.fetchall()]
            products = self.env['product.product'].browse(product_ids)
            template_ids = products.mapped('product_tmpl_id').ids

        return product_ids, template_ids

    @api.depends('order_id.partner_id', 'order_id.warehouse_id')
    def _compute_allowed_product_templates(self):
        for line in self:
            _, template_ids = line._get_available_product_and_template_ids()
            line.allowed_product_ids = [(6, 0, template_ids)]

    @api.onchange('order_id.partner_id', 'order_id.warehouse_id')
    def _onchange_order_warehouse_product_domain(self):
        order = self.order_id

        if not order or not order.partner_id or not order.warehouse_id:
            self.product_id = False
            return {
                'domain': {'product_id': [('id', '=', 0)]},
                'warning': {
                    'title': "Missing Information",
                    'message': "Please select a customer and warehouse to see available products."
                }
            }

        product_ids, _ = self._get_available_product_and_template_ids()

        if not product_ids:
            self.product_id = False
            return {
                'domain': {'product_id': [('id', '=', 0)]},
                'warning': {
                    'title': "No Available Products",
                    'message': f"No products available in warehouse: {order.warehouse_id.display_name}"
                }
            }

        if self.product_id and self.product_id.id not in product_ids:
            self.product_id = False

        return {
            'domain': {'product_id': [('id', 'in', product_ids)]}
        }
