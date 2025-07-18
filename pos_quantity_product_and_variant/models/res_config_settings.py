from odoo import models, fields

class ResConfigSettiongsInhert(models.TransientModel):
    _inherit = "res.config.settings"

    pos_show_only_available_products = fields.Boolean(related="pos_config_id.show_only_available_products", readonly=False)

    pos_show_product_qty = fields.Boolean(related="pos_config_id.show_product_qty", readonly=False)
    pos_show_on_hand_qty = fields.Boolean(related="pos_config_id.show_on_hand_qty", readonly=False)
    pos_show_virtual_qty = fields.Boolean(related="pos_config_id.show_virtual_qty", readonly=False)
