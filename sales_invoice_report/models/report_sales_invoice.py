from odoo import models

class ReportSalesInvoice(models.AbstractModel):
    _name = 'report.sales_invoice_report.report_invoice_template'
    _description = 'Custom Sales Invoice Report'

    def _get_report_values(self, docids, data=None):
        # Fetch the invoices from the passed data
        invoices = data.get('docs') if data else []
        return {
            'docs': invoices,
            'wizard_data': data.get('wizard_data') if data else {},
        }
