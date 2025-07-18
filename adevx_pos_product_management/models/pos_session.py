from odoo import api, fields, models


class PosSession(models.Model):
    _inherit = 'pos.session'



    @api.model
    def _load_pos_data_models(self, config_id):
        data = super()._load_pos_data_models(config_id)
        loc_model = 'stock.location'
        if loc_model not in data:
            data.append(loc_model)
        data += [ "product.attribute.value"]
        return data




