from odoo import api, fields, models


class ProductAttributeValue(models.Model):
    _name = 'product.attribute.value'
    _inherit = ['product.attribute.value', 'pos.load.mixin']

    @api.model
    def _load_pos_data_domain(self, data):
        return []

    @api.model
    def _load_pos_data_fields(self, config_id):
        params = super()._load_pos_data_fields(config_id)
        params += ['name', 'attribute_id']
        return params

    def _load_pos_data(self, data):
        config_data = data.get('pos.config', {}).get('data', [{}])[0]
        if config_data.get('invoice_screen', False):
            domain = self._load_pos_data_domain(data)
            fields = self._load_pos_data_fields(config_data.get('id'))

            return {
                'data': self.search_read(domain, fields, load=False),
                'fields': fields,
                'relations': {},  # ensure compatibility
            }

        return {
            'data': [],
            'fields': [],
            'relations': {},
        }


