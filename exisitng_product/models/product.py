from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    similar_product_ids = fields.One2many(
        'product.template',
        compute='_compute_similar_products',
        string="Similar Products",
        help="List of existing products with similar names"
    )

    @api.depends('name')
    def _compute_similar_products(self):
        for rec in self:
            if rec.name:
                rec.similar_product_ids = self.env['product.template'].search([
                    ('name', 'ilike', rec.name),
                    ('id', '!=', rec.id),
                ])
            else:
                rec.similar_product_ids = False
