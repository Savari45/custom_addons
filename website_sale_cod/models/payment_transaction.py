from odoo import models

class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _reconcile_after_done(self):
        res = super()._reconcile_after_done()
        for tx in self:
            if tx.sale_order_ids and tx.provider_id and tx.provider_id.code == 'custom_cod':
                tx.sale_order_ids.write({'is_cod': True})
        return res
