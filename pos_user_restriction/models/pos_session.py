from odoo import models

class PosSession(models.Model):
    _inherit = 'pos.session'

    def _loader_params_product_product(self):
        res = super()._loader_params_product_product()
        fields = res['search_params']['fields']
        if 'available_qty_in_pos' not in fields:
            fields.append('available_qty_in_pos')
        if 'available_in_pos' not in fields:
            fields.append('available_in_pos')
        return res

    def _load_product_product(self, config):
        # This works fine since available_in_pos is now stored
        products = super()._load_product_product(config)
        return [p for p in products if p.get('available_in_pos')]
