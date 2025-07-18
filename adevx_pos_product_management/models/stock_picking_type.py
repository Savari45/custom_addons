from odoo import api, fields, models


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    @api.model
    def _load_pos_data_fields(self, config_id):
        params = super()._load_pos_data_fields(config_id)
        params += ["default_location_src_id"]
        return params


