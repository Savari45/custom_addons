from odoo import api, fields, models


class ProductTemplateAttributeValue(models.Model):
    _inherit = 'product.template.attribute.value'

    @api.model
    def _load_pos_data_fields(self, config_id):
        params = super()._load_pos_data_fields(config_id)
        params += [
            "product_tmpl_id"
        ]
        return params
