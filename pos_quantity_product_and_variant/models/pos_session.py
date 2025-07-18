from collections import defaultdict
from odoo import models


class PosSession(models.Model):
    _inherit = 'pos.session'

    def get_available_product_quantities(self):
        locations = self.env['stock.location'].search([('id', '=', self.config_id.picking_type_id.default_location_src_id.id)])
        all_locations = list(locations.child_internal_location_ids.ids)

        stocked_products = self.env['stock.quant'].search([('location_id', 'in', all_locations), ('quantity', '>', 0)])
        available_product_ids = stocked_products.mapped('product_id')

        available_product_quantities = defaultdict(list)
        for product in available_product_ids:
            stocked_products = self.env['stock.quant'].search([
                ('product_id', '=', product.id),
                ('location_id', '=', self.config_id.picking_type_id.default_location_src_id.id), ('quantity', '>', 0)
            ])
            available_product_quantities[product.product_tmpl_id.id].append((product.id, sum(stocked_products.mapped('quantity'))))

        return available_product_quantities
    
    def get_product_info(self):
        products = self.env['product.product'].search([])
        product_info = {}
        for product in products:
            product_info[product.id] = {
                "variant_name": product.product_template_attribute_value_ids._get_combination_name(),
                "qty_available": product.qty_available,
                "virtual_available": product.virtual_available,
                "type": product.type,
            }
        return product_info
    
    def get_product_mapping(self):
        products = self.env['product.product'].search([])
        return {product.id: product.product_tmpl_id.id for product in products}
