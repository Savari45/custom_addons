from odoo import models, fields


class PosConfig(models.Model):
    _inherit = 'pos.config'

    show_only_available_products = fields.Boolean(string='Show Only Available Products', default=False)

    show_product_qty = fields.Boolean(string='Display Stock Quantities', default=True)
    show_on_hand_qty = fields.Boolean(string='Display On Hand Quantity', default=True)
    show_virtual_qty = fields.Boolean(string='Display Virtual Quantity', default=False)
