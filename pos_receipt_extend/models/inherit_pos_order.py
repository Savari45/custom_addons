from odoo import fields, models,api



class PosOrder(models.Model):
    _inherit = 'pos.order'

    account_move_name = fields.Char(string='Invoice Number', compute='_compute_account_move_name', store=False)
    account_move_code = fields.Char(string='sign code')
    invoice_date_str = fields.Char(string='Invoice Date')
    def _compute_account_move_name(self):
        for order in self:
            order.account_move_name = order.account_move.name if order.account_move else ''
            order.account_move_code = order.account_move.signature_code

class PosSession(models.Model):
    _inherit = 'pos.session'
    @api.model
    def _loader_params_pos_order(self):
        result = super()._loader_params_pos_order()
        result['search_params']['fields'].extend(['account_move_name', 'account_move_code'])
        print('result',result)
        return result