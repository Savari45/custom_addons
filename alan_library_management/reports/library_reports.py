from odoo import models, fields, api
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

class BookReport(models.AbstractModel):
    _name = 'report.alan_library_management.book_report'
    _description = 'Book Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['library.book'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'library.book',
            'docs': docs,
            'generated_on': datetime.now().strftime('%Y-%m-%d %H:%M'),
        }

    def _get_availability(self, book):
        return book.available_quantity

class MemberReport(models.AbstractModel):
    _name = 'report.alan_library_management.member_report'
    _description = 'Library Member Report'

    def _get_report_values(self, docids, data=None):
        docs = self.env['library.member'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'library.member',
            'docs': docs,
            # 'datetime': datetime,
            'dt': datetime.now().strftime('%Y-%m-%d %H:%M'),
        }


class TransactionReportWizard(models.TransientModel):
    _name = 'library.transaction.report.wizard'
    _description = 'Transaction Report Wizard'

    date_from = fields.Date(string='From Date')
    date_to = fields.Date(string='To Date', default=fields.Date.today)
    state = fields.Selection([
        ('borrowed', 'Borrowed'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
        ('lost', 'Lost'),
        ('all', 'All'),
    ], string='Status', default='all')

    def action_print_report(self):
        self.ensure_one()
        return self.env.ref('alan_library_management.action_report_library_transaction').report_action(self)


class TransactionReport(models.AbstractModel):
    _name = 'report.alan_library_management.transaction_report'
    _description = 'Transaction Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        wizard = self.env['library.transaction.report.wizard'].browse(docids).ensure_one()

        domain = []

        # Smart handling of filters
        if wizard.date_from:
            domain.append(('borrow_date', '>=', wizard.date_from))
        if wizard.date_to:
            domain.append(('borrow_date', '<=', wizard.date_to))
        if wizard.state and wizard.state != 'all':
            domain.append(('state', '=', wizard.state))

        _logger.info(f"[Transaction Report] Domain: {domain}")

        transactions = self.env['library.transaction'].search(domain, order='borrow_date asc')

        _logger.info(f"[Transaction Report] {len(transactions)} transaction(s) found")

        transaction_data = []
        for t in transactions:
            transaction_data.append({
                'id': t.id,
                'book_name': t.book_id.name if t.book_id else 'No Book',
                'member_name': t.member_id.name if t.member_id else 'No Member',
                'borrow_date': t.borrow_date.strftime('%Y-%m-%d %H:%M') if t.borrow_date else 'N/A',
                'expected_return_date': t.expected_return_date.strftime('%Y-%m-%d %H:%M') if t.expected_return_date else 'N/A',
                'actual_return_date': t.actual_return_date.strftime('%Y-%m-%d %H:%M') if t.actual_return_date else 'Not returned',
                'state': t.state.capitalize() if t.state else 'Unknown',
                'fine_amount': "%.2f" % t.fine_amount if t.fine_amount else "0.00",
            })

        # Remove dummy data (now that real ones are fetched)
        return {
            'doc_ids': docids,
            'doc_model': 'library.transaction.report.wizard',
            'transactions': transaction_data,
            'date_from': wizard.date_from.strftime('%Y-%m-%d') if wizard.date_from else 'All',
            'date_to': wizard.date_to.strftime('%Y-%m-%d') if wizard.date_to else 'All',
            'state': wizard.state.capitalize() if wizard.state and wizard.state != 'all' else 'All',
            'current_date': fields.Date.today().strftime('%Y-%m-%d'),
            'company': self.env.company,
            'transaction_count': len(transaction_data),
        }