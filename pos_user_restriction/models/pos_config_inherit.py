from odoo import models

class PosConfig(models.Model):
    _inherit = 'pos.config'

    def _pos_ui_models_to_load(self):
        result = super()._pos_ui_models_to_load()
        result += ['res.users', 'stock.quant', 'stock.warehouse']
        return result

    def _loader_params_res_users(self):
        return {
            'search_params': {
                'fields': ['name', 'property_warehouse_id'],
            },
        }

    def _get_pos_ui_res_users(self, params):
        users = self.env['res.users'].search_read(**params['search_params'])
        print(">>> RES USERS LOADED FOR POS:", users)
        return users
    def _loader_params_stock_quant(self):
        return {
            'search_params': {
                'domain': [('quantity', '>', 0)],
                'fields': ['product_id', 'location_id', 'quantity'],
            },
        }

    def _get_pos_ui_stock_quant(self, params):
        quants = self.env['stock.quant'].search_read(**params['search_params'])
        print(">>> STOCK QUANTS:", quants[:5])  # Show first 5 for debug
        return quants
    def _loader_params_stock_warehouse(self):
        return {'search_params': {'fields': ['name', 'lot_stock_id']}}

    def _get_pos_ui_stock_warehouse(self, params):
        warehouses = self.env['stock.warehouse'].search_read(**params['search_params'])
        print(">>> STOCK WAREHOUSES:", warehouses)
        return warehouses