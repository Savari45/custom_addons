from odoo import models, fields

class SalesInvoiceReportWizard(models.TransientModel):
    _name = 'sales.invoice.report.wizard'
    _description = 'Sales Invoice Report Wizard'

    date_from = fields.Date(string="From Date")
    date_to = fields.Date(string="To Date")
    partner_id = fields.Many2one('res.partner', string="Customer")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('posted', 'Posted'),
        ('paid', 'Paid'),
        ('not_paid', 'Unpaid'),
        ('overdue', 'Overdue'),
    ], string="Invoice Status")

    def action_print_report(self):
        invoices = self._get_filtered_invoices()
        data = {
            'docs': invoices,
            'wizard_data': {
                'date_from': self.date_from,
                'date_to': self.date_to,
                'partner_id': self.partner_id.id,
                'state': self.state,
            },
        }
        return self.env.ref('custom_invoice_report.invoice_report_pdf').report_action(self,data=data)

    def _get_filtered_invoices(self):
        domain = []
        if self.date_from:
            domain.append(('invoice_date', '>=', self.date_from))
        if self.date_to:
            domain.append(('invoice_date', '<=', self.date_to))
        if self.partner_id:
            domain.append(('partner_id', '=', self.partner_id.id))
        if self.state:
            if self.state == 'not_paid':
                domain.append(('payment_state', '=', 'not_paid'))
            elif self.state == 'paid':
                domain.append(('payment_state', '=', 'paid'))
            elif self.state == 'overdue':
                domain.append(('invoice_date_due', '<', fields.Date.today()))
                domain.append(('payment_state', '!=', 'paid'))

        return self.env['account.move'].search(domain)

