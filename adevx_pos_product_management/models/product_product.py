import json

from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    product_tmpl_name = fields.Char(related='product_tmpl_id.display_name', string='Template Name', store=True)
    #
    # @api.depends('name', 'default_code', 'product_tmpl_id')
    # @api.depends_context('display_default_code', 'seller_id', 'company_id', 'partner_id')
    # def _compute_display_name(self):
    #     self.env.context = dict(self.env.context)
    #     self.env.context.update({
    #         'display_default_code': False
    #     })
    #     super()._compute_display_name()
    #     for rec in self:
    #         if rec.display_name:
    #             rec.display_name = f'[{rec.default_code}] {rec.display_name}'

    @api.model
    def _load_pos_data_fields(self, config_id):
        params = super()._load_pos_data_fields(config_id)
        params += [
            "qty_available",
            "product_variant_count",
            "product_tmpl_name"
        ]
        return params