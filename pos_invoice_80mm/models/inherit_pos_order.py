from odoo import models, api, _
from odoo.exceptions import UserError
import base64

class PosOrder(models.Model):
    _inherit = 'pos.order'

    def _generate_pos_order_invoice(self):
        moves = self.env['account.move']

        for order in self:
            if order.account_move:
                moves += order.account_move
                continue

            if not order.partner_id:
                raise UserError(_('Please provide a partner for the sale.'))

            move_vals = order._prepare_invoice_vals()
            new_move = order._create_invoice(move_vals)

            order.state = 'invoiced'
            new_move.sudo().with_company(order.company_id).with_context(skip_invoice_sync=True)._post()
            moves += new_move

            payment_moves = order._apply_invoice_payments(order.session_id.state == 'closed')

            if self.env.context.get('generate_pdf', True):
                # Changed the variable name from _ to something else
                pdf_content, dummy = self.env['ir.actions.report']._render_qweb_pdf(
                    'pos_invoice_80mm.action_report_pos_invoice',
                    res_ids=new_move.ids
                )
                filename = f"{new_move.name}-80mm.pdf"

                self.env['ir.attachment'].create({
                    'name': filename,
                    'type': 'binary',
                    'datas': base64.b64encode(pdf_content),
                    'res_model': 'account.move',
                    'res_id': new_move.id,
                    'mimetype': 'application/pdf',
                })

            if order.session_id.state == 'closed':
                order._create_misc_reversal_move(payment_moves)

        if not moves:
            return {}

        return {
            'name': _('Customer Invoice'),  # Now _ is preserved as the translation function
            'view_mode': 'form',
            'view_id': self.env.ref('account.view_move_form').id,
            'res_model': 'account.move',
            'context': "{'move_type':'out_invoice'}",
            'type': 'ir.actions.act_window',
            'target': 'current',
            'res_id': moves and moves.ids[0] or False,
        }