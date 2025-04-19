from odoo import models, fields, api

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    purchase_order_id = fields.Many2one('purchase.order', string="Linked Purchase Order")

    def action_post(self):
        """Overrides action_post to reconcile payments automatically"""
        res = super().action_post()
        if self.purchase_order_id:
            self.purchase_order_id.advance_payment_approved = True
        return res
