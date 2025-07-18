# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResConfig(models.TransientModel):
    """
    This is an Odoo model for configuration settings. It inherits from the
    'res.config.settings' model and extends its functionality by adding
    fields for low stock alert configuration

    """
    _inherit = 'res.config.settings'

    is_low_stock_alert_individual = fields.Boolean(
        string="Low Stock Alert For Individual Product",
        help='This field determines the minimum stock quantity at which a low '
             'stock alert will be triggered.When the product quantity falls '
             'below this value, the background color for the product will be '
             'changed based on the alert state.',
        config_parameter='low_stocks_product_alert.is_low_stock_alert_individual',
        default=False)


    def set_values(self):
        super().set_values()
        if self.is_low_stock_alert_individual:
            products = self.env['product.product'].search([])
            products.write({'is_low_stock_alert': True})
        else:
            products = self.env['product.product'].search([])
            products.write({'is_low_stock_alert': False})