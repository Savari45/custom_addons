from odoo import models, api

class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.onchange('location_id')
    def _onchange_location_id_internal_transfer(self):
        for move in self:
            if move.location_id and move.picking_id.picking_type_id.code == 'internal':
                Product = self.env['product.product']
                StockQuant = self.env['stock.quant']

                available_products = Product.search([]).filtered(
                    lambda p: StockQuant._get_available_quantity(p, move.location_id) > 0
                )

                # Force recompute display_name just for this context
                available_products.with_context(
                    location_id=move.location_id.id,
                    custom_display_stock_move=True
                )._compute_display_name()

                return {
                    'domain': {
                        'product_id': [('id', 'in', available_products.ids)],
                    },
                    'context': {
                        'location_id': move.location_id.id,
                        'custom_display_stock_move': True,
                    }
                }
