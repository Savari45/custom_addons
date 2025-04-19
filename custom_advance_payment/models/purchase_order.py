from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    advance_payment_approved = fields.Boolean(string="Advance Payment Approved", default=False)
    advance_payment_id = fields.Many2one('account.payment', string="Advance Payment")

    def action_request_advance_payment(self):
        """Function to open the Advance Payment form when clicking the button"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Advance Payment',
            'res_model': 'account.payment',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_partner_id': self.partner_id.id,
                'default_amount': self.amount_total,
                'default_payment_type': 'outbound',
                'default_payment_method_id': self.env.ref('account.account_payment_method_manual_out').id
            }
        }

    def action_create_advance_payment(self):
        """Function to create and confirm Advance Payment"""
        payment = self.env['account.payment'].create({
            'partner_id': self.partner_id.id,
            'amount': self.amount_total,
            'payment_type': 'outbound',
            'payment_method_id': self.env.ref('account.account_payment_method_manual_out').id
        })
        payment.action_post()
        self.advance_payment_id = payment.id
        self.advance_payment_approved = True
