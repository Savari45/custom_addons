import io
import base64
import xlsxwriter
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_quotation_send(self):
        """ Opens a wizard to compose an email, with Excel file attached instead of default PDF """
        self.filtered(lambda so: so.state in ('draft', 'sent')).order_line._validate_analytic_distribution()
        lang = self.env.context.get('lang')

        ctx = {
            'default_model': 'sale.order',
            'default_res_ids': self.ids,
            'default_composition_mode': 'comment',
            'default_email_layout_xmlid': 'mail.mail_notification_layout_with_responsible_signature',
            'email_notification_allow_footer': True,
            'proforma': self.env.context.get('proforma', False),
        }

        if len(self) > 1:
            ctx['default_composition_mode'] = 'mass_mail'
        else:
            ctx.update({
                'force_email': True,
                'model_description': self.with_context(lang=lang).type_name,
            })
            if not self.env.context.get('hide_default_template'):
                mail_template = self._find_mail_template()
                if mail_template:
                    ctx.update({
                        'default_template_id': mail_template.id,
                        'mark_so_as_sent': True,
                    })
                    if mail_template.lang:
                        lang = mail_template._render_lang(self.ids)[self.id]
            else:
                for order in self:
                    order._portal_ensure_token()

        # Generate and attach Excel file
        attachment_ids = []
        for order in self:
            attachment = order._generate_excel_attachment()
            if attachment:
                attachment_ids.append(attachment.id)

        if attachment_ids:
            ctx['default_attachment_ids'] = [(4, att_id) for att_id in attachment_ids]

        action = {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }

        if (
            self.env.context.get('check_document_layout')
            and not self.env.context.get('discard_logo_check')
            and self.env.is_admin()
            and not self.env.company.external_report_layout_id
        ):
            layout_action = self.env['ir.actions.report']._action_configure_external_report_layout(action)
            action.pop('close_on_report_download', None)
            layout_action['context']['dialog_size'] = 'extra-large'
            return layout_action

        return action

    def _find_mail_template(self):
        self.ensure_one()
        if self.env.context.get('proforma') or self.state != 'sale':
            return self.env.ref('sale.email_template_edi_sale', raise_if_not_found=False)
        else:
            return self._get_confirmation_template()

    def _get_confirmation_template(self):
        self.ensure_one()
        default_confirmation_template_id = self.env['ir.config_parameter'].sudo().get_param(
            'sale.default_confirmation_template'
        )
        default_confirmation_template = default_confirmation_template_id and \
            self.env['mail.template'].browse(int(default_confirmation_template_id)).exists()
        if default_confirmation_template:
            return default_confirmation_template
        return self.env.ref('sale.mail_template_sale_confirmation', raise_if_not_found=False)

    def action_quotation_sent(self):
        if any(order.state != 'draft' for order in self):
            raise UserError(_("Only draft orders can be marked as sent directly."))

        for order in self:
            order.message_subscribe(partner_ids=order.partner_id.ids)

        self.write({'state': 'sent'})

    def _generate_excel_attachment(self):
        """Generate Excel file from the sale order and return ir.attachment record"""
        self.ensure_one()
        buffer = io.BytesIO()
        workbook = xlsxwriter.Workbook(buffer, {'in_memory': True})
        sheet = workbook.add_worksheet("Quotation")

        bold = workbook.add_format({'bold': True})
        currency = workbook.add_format({'num_format': '₹#,##0.00'})

        headers = ['Product', 'Description', 'Quantity', 'Unit Price', 'Subtotal']
        for col, header in enumerate(headers):
            sheet.write(0, col, header, bold)

        row = 1
        for line in self.order_line:
            sheet.write(row, 0, line.product_id.display_name)
            sheet.write(row, 1, line.name or '')
            sheet.write(row, 2, line.product_uom_qty)
            sheet.write(row, 3, line.price_unit, currency)
            sheet.write(row, 4, line.price_subtotal, currency)
            row += 1

        sheet.write(row + 1, 3, 'Total:', bold)
        sheet.write(row + 1, 4, self.amount_total, currency)

        workbook.close()
        buffer.seek(0)

        return self.env['ir.attachment'].create({
            'name': f'{self.name}.xlsx',
            'type': 'binary',
            'datas': base64.b64encode(buffer.read()),
            'res_model': 'sale.order',
            'res_id': self.id,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        })
