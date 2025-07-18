# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    is_low_stock_alert = fields.Boolean(
        string="Low Stock Alert",
        help='Enable this to trigger a low stock warning when quantity drops below the specified threshold.'
    )

    min_low_stock_alert = fields.Integer(
        string='Alert Quantity',
        help='The minimum quantity before a low stock alert is shown.'
    )
    stock_quantity = fields.Float(
        string="Stock Quantity (POS)",
        compute="_compute_stock_quantity",
        help="Temporary field used in POS frontend for stock display."
    )

    @api.depends('qty_available')
    def _compute_stock_quantity(self):
        for product in self:
            product.stock_quantity = product.qty_available

    @api.model
    def _load_pos_data_fields(self, config_id):
        """Extend POS loaded product fields"""
        fields = super(ProductProduct, self)._load_pos_data_fields(config_id)
        fields.append('qty_available')  # Correct field to show available quantity
        fields.append('min_low_stock_alert')  # Field for low stock comparison
        return fields

    @api.model
    def nt_get_product_info_pos(self, location_id, product_ids):
        """
        Return quantities of given products at a specific location.

        :param location_id: ID of stock.location
        :param product_ids: List of product.product IDs
        :return: Dict {product_id: quantity}
        """
        quantities = {}

        # Group stock quantities by product
        stock_quantities = self.env['stock.quant'].sudo().read_group(
            [('product_id', 'in', product_ids), ('location_id', '=', location_id)],
            ['product_id', 'quantity'],
            ['product_id']
        )

        # Map to dict: product_id -> quantity
        for quant in stock_quantities:
            product_id = quant['product_id'][0]
            quantities[product_id] = quant['quantity']

        # Ensure all product_ids are represented
        for product_id in product_ids:
            if product_id not in quantities:
                quantities[product_id] = 0.0

        return quantities
