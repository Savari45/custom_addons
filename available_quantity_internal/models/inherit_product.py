from odoo import models, api

class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.depends('name', 'default_code', 'product_template_attribute_value_ids')
    def _compute_display_name(self):
        # Always fallback to normal name
        for product in self:
            product.display_name = product.name
            variant = product.product_template_attribute_value_ids._get_combination_name()
            if variant:
                product.display_name = f"{product.name} ({variant})"
            if product.default_code:
                product.display_name = f"[{product.default_code}] {product.display_name}"

            # Custom for stock.move ONLY
            if self.env.context.get('custom_display_stock_move') and self.env.context.get('location_id'):
                location = self.env['stock.location'].browse(self.env.context['location_id'])
                qty = self.env['stock.quant']._get_available_quantity(product, location)
                product.display_name += f" - {int(qty or 0)}"
