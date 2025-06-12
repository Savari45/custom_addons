from odoo import models, fields, api
from odoo.fields import Image
from odoo.exceptions import UserError

class LibraryBook(models.Model):
    _name = 'library.book'
    _description = 'Library Book'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _barcode_field = 'barcode'

    name = fields.Char(string='Title', required=True, tracking=True)
    isbn = fields.Char(string='ISBN', tracking=True)
    author_ids = fields.Char(string='Authors', required=True) # widget="many2many_tags"
    publisher = fields.Char(string='Publisher', required=True)
    publishing_year = fields.Char(string="Publishing Year")
    category_id = fields.Many2one(
        'library.book.category',
        string='Category',
        ondelete='restrict'  # prevent deletion if referenced
    )
    barcode = fields.Char(string="Barcode", copy=False, index=True)
    transaction_ids = fields.One2many(
        'library.transaction',
        'book_id',
        string='Transactions'
    )
    pages = fields.Integer(string='Number of Pages')
    edition = fields.Char(string='Edition')
    quantity = fields.Integer(string='Total Copies', default=1)
    available_quantity = fields.Integer(
        string='Available Copies',
        compute='_compute_available_quantity',
        store=True # add this to store the computed value
        ,readonly = False
    )
    qty = fields.Char(string='Quantity Status', compute='_compute_qty', store=False)
    image = fields.Image("Book Cover")
    active = fields.Boolean(string='Active', default=True)
    description = fields.Text(string='Description')
    shelf_location = fields.Char(string='Shelf Location')
    state = fields.Selection([
        ('available', 'Available'),
        ('lost', 'Lost'),
        ('damaged', 'Damaged'),
    ], string='Status', default='available', tracking=True)
    display_status = fields.Char(string="Display Status", compute="_compute_display_status")
    barcode = fields.Char(string="Barcode", required=True, unique=True)

    @api.model_create_multi
    def create(self, vals_list):
        """
        Override create to auto-generate barcodes for new books
        Handles both single and batch creation
        """
        # Handle both single record and batch creation
        if not isinstance(vals_list, list):
            vals_list = [vals_list]

        for vals in vals_list:
            if not vals.get('barcode'):
                vals['barcode'] = self.env['ir.sequence'].next_by_code(
                    'library.book.barcode') or f"BOOK-{fields.Datetime.now().strftime('%Y%m%d%H%M%S')}"

        return super(LibraryBook, self).create(vals_list)

    @api.depends('state', 'available_quantity')
    def _compute_display_status(self):
        for record in self:
            if record.available_quantity == 0:
                record.display_status = "Unavailable"
            else:
                record.display_status = dict(self._fields['state'].selection).get(record.state, "Unknown")

    @api.depends('quantity', 'available_quantity')
    def _compute_qty(self):
        for record in self:
            record.qty = f"{record.available_quantity}/{record.quantity}"

    @api.depends('quantity', 'transaction_ids.state')
    def _compute_available_quantity(self):
        for book in self:
            loaned = len(book.transaction_ids.filtered(
                lambda t: t.state == 'borrowed'
            ))
            book.available_quantity = book.quantity - loaned

    def get_loan_data(self):
        self.ensure_one()
        loan_list = []
        today = fields.Date.today()

        for loan in self.transaction_ids.filtered(lambda l: l.state == 'borrowed'):
            due_datetime = loan.expected_return_date
            due_date = due_datetime.date() if due_datetime else None

            loan_list.append({
                'member': loan.member_id.display_name,
                'borrow_date': loan.borrow_date,
                'due_date': loan.expected_return_date,
                'is_overdue': due_date and due_date < today
            })

        return loan_list

