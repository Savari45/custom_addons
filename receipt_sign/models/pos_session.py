from odoo import models,fields, api

class PosOrder(models.Model):
    _inherit = 'pos.order'

    signature_code = fields.Char(string='Signature Code', compute='_compute_signature_code')
    @api.depends('account_move')
    def _compute_signature_code(self):
        print('fffffffffffffffffffff')
        for order in self:
            order.signature_code = order.account_move.signature_code if order.account_move else False
            print(order.signature_code)
class PosSession(models.Model):
    _inherit = 'pos.session'

    @api.model
    def _pos_data_process(self, loaded_data):
        print('posssssssssssssession')
        super()._pos_data_process(loaded_data)

        # Manually fetch signature_code for all POS orders
        order_ids = [order['id'] for order in loaded_data.get('pos.orders', [])]
        if order_ids:
            orders_with_code = self.env['pos.order'].search_read(
                [('id', 'in', order_ids)],
                ['id', 'signature_code']
            )
            # Map signature_code to loaded orders
            code_mapping = {order['id']: order['signature_code'] for order in orders_with_code}
            print(code_mapping)
            for order in loaded_data['pos.orders']:
                order['signature_code'] = code_mapping.get(order['id'], False)

        return loaded_data