from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_cod = fields.Boolean(string="Cash on Delivery")
