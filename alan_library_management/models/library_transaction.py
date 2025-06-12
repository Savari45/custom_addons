from odoo import models, fields, api
from datetime import datetime, timedelta
from odoo.exceptions import UserError

class LibraryTransaction(models.Model):
    _name = 'library.transaction'
    _description = 'Library Transaction'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'barcodes.barcode_events_mixin']
    _order = 'borrow_date desc'

    book_id = fields.Many2one('library.book', string='Book')
    member_id = fields.Many2one('library.member', string='Member')
    borrow_date = fields.Datetime(string='Borrow Date', default=fields.Datetime.now)
    expected_return_date = fields.Datetime(string='Expected Return Date', compute='_compute_expected_return_date',
                                           store=True)
    actual_return_date = fields.Datetime(string='Actual Return Date')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('borrowed', 'Borrowed'),
        ('returned', 'Returned'),
        ('lost', 'Lost'),
        ('overdue', 'Overdue'),
    ], string='Status', default='draft', tracking=True)
    fine_amount = fields.Float(string='Fine Amount', compute='_compute_fine_amount', store=True)
    notes = fields.Text(string='Notes')
    scanned_barcode = fields.Char(string="Scanned Barcode", copy=False)

    # Barcode scanning methods
    def on_barcode_scanned(self, barcode):
        self.ensure_one()
        self.scanned_barcode = barcode
        self.process_barcode(barcode)

    def process_barcode(self, barcode, scan_type):
        """ Process scanned barcode for either book or member """
        self.ensure_one()

        if scan_type == 'book':
            book = self.env['library.book'].search([('barcode', '=', barcode)], limit=1)
            if book:
                self.book_id = book
                return {'success': True, 'message': f'Book found: {book.name}'}
            return {'success': False, 'message': 'No book found with this barcode'}

        elif scan_type == 'member':
            member = self.env['library.member'].search([('barcode', '=', barcode)], limit=1)
            if member:
                self.member_id = member
                return {'success': True, 'message': f'Member found: {member.name}'}
            return {'success': False, 'message': 'No member found with this barcode'}

    def action_open_book_scanner(self):
        """ Open scanner for books """
        return {
            'name': 'Scan Book Barcode',
            'type': 'ir.actions.act_window',
            'res_model': 'library.barcode.scanner.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('alan_library_management.view_book_barcode_scanner_wizard_form').id,
            'target': 'new',
            'context': {
                'default_transaction_id': self.id,
                'default_scan_type': 'book',
            }
        }

    def action_open_member_scanner(self):
        """ Open scanner for members """
        return {
            'name': 'Scan Member Barcode',
            'type': 'ir.actions.act_window',
            'res_model': 'library.barcode.scanner.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('alan_library_management.view_member_barcode_scanner_wizard_form').id,
            'target': 'new',
            'context': {
                'default_transaction_id': self.id,
                'default_scan_type': 'member',
            }
        }

    @api.depends('borrow_date')
    def _compute_expected_return_date(self):
        for record in self:
            if record.borrow_date:
                borrow_date = fields.Datetime.from_string(record.borrow_date)
                record.expected_return_date = borrow_date + timedelta(days=14)

    @api.depends('actual_return_date', 'expected_return_date', 'state')
    def _compute_fine_amount(self):
        for record in self:
            today = fields.Datetime.now()
            record.fine_amount = 0  # Reset fine amount

            if record.expected_return_date:
                expected_date = fields.Datetime.from_string(record.expected_return_date)

                # Case 1: Book was returned late
                if record.actual_return_date:
                    return_date = fields.Datetime.from_string(record.actual_return_date)
                    if return_date > expected_date:
                        delta = return_date - expected_date
                        record.fine_amount = delta.days * 10

                # Case 2: Book not returned and overdue
                elif record.state == 'borrowed' and today > expected_date:
                    delta = today - expected_date
                    record.fine_amount = delta.days * 10

                # Case 3: Book marked as lost
                elif record.state == 'lost':
                    delta = today - expected_date
                    record.fine_amount = delta.days * 10 if today > expected_date else 0

    def update_overdue_fines(self):
        """ Scheduled action to update fines daily """
        overdue_transactions = self.search([
            ('state', '=', 'borrowed'),
            ('expected_return_date', '<', fields.Datetime.now())
        ])
        overdue_transactions._compute_fine_amount()

    def action_borrow(self):
        for record in self:
            if record.book_id.available_quantity <= 0:
                raise UserError('No available copies of this book to borrow.')
            record.state = 'borrowed'

    def action_return(self):
        for record in self:
            record.actual_return_date = fields.Datetime.now()
            record.state = 'returned'

    def action_lost(self):
        for record in self:
            record.state = 'lost'
            record.book_id.quantity -= 1

    @api.onchange('book_id')
    def _onchange_book_id(self):
        if self.book_id and self.book_id.available_quantity <= 0:
            self.book_id = False  # Reset the book selection
            return {
                'warning': {
                    'title': 'Book Unavailable',
                    'message': 'This book is currently unavailable for borrowing.',
                }
            }
