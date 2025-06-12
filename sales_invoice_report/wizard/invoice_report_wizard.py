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
        print(invoices)
        return self.env.ref('sales_invoice_report.invoice_report_pdf').report_action(
            invoices,  # <-- pass recordset here as docids
            data={
                'wizard_data': {
                    'date_from': self.date_from,
                    'date_to': self.date_to,
                    'partner_id': self.partner_id.id,
                    'state': self.state,
                },
            }
        )

    def _get_filtered_invoices(self):
        print("welcome filter")
        domain = [('move_type', '=', 'out_invoice')]
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
        print(domain)
        return self.env['account.move'].search(domain)

