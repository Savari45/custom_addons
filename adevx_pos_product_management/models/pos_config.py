from odoo import api, fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    display_onhand = fields.Boolean(
        string="Show Stock on Hand each Product", default=True,
        help="Display quantity on hand all products on pos screen")
    allow_order_out_of_stock = fields.Boolean(
        string="Allow Order when Product Out Of Stock",
        help="If uncheck, any product out of stock will blocked sale",
        default=True)
    update_stock_onhand = fields.Boolean(string="Allow Update Stock On Hand", default=False)
    multi_location = fields.Boolean(string="Update Stock each Location", default=False)
    show_multi_location_info = fields.Boolean(string="Show Stock each Location In Info", default=True)
    stock_location_ids = fields.Many2many(
        comodel_name="stock.location", string="Stock Locations",
        relation='pos_product_management_stock_location_ids_rel',
        help="Stock Locations for cashier select checking stock on hand \n"
             "and made picking source location from location selected",
        domain=[("usage", "=", "internal")])
    limit_products_loading = fields.Boolean(string="Limit Products loading")
    limit_products_loading_count = fields.Integer(string="Limit Products loading Count", default=20000)

    def get_limited_product_count(self):
        if self.limit_products_loading:
            return self.limit_products_loading_count + 1
        return super().get_limited_product_count()
