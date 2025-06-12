from odoo import models, fields, api
import random
import string
from datetime import datetime, timedelta
import logging
from odoo.exceptions import UserError
import base64
import io
import qrcode

_logger = logging.getLogger(__name__)

class LibraryMember(models.Model):
    _name = 'library.member'
    _description = 'Library Member'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'partner_id'  # This will show the partner's name by default
    _barcode_field = 'barcode'

    partner_id = fields.Many2one('res.partner', string='Name', required=True)
    name = fields.Char(related='partner_id.name', string='Member Name', store=True)
    membership_number = fields.Char(
        string='Membership Number',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: self._generate_membership_number(),
        tracking=True
    )
    barcode = fields.Char(string="Barcode", copy=False, index=True)
    membership_start = fields.Date(string='Membership Start Date', default=fields.Date.today)
    membership_end = fields.Date(string='Membership End Date')
    active = fields.Boolean(string='Active', default=True)
    image = fields.Binary(related='partner_id.image_1920', string='Image', readonly=False, attachment=True, store=True)
    phone = fields.Char(related='partner_id.phone', string='Phone', readonly=False)
    email = fields.Char(related='partner_id.email', string='Email', readonly=False)
    # address = fields.Char(related='partner_id.contact_address', string='Address', readonly=False)
    street = fields.Char(related='partner_id.street', readonly=False)
    street2 = fields.Char(related='partner_id.street2', readonly=False)
    city = fields.Char(related='partner_id.city', readonly=False)
    state_id = fields.Many2one(related='partner_id.state_id', readonly=False)
    country_id = fields.Many2one(related='partner_id.country_id', readonly=False)
    zip = fields.Char(related='partner_id.zip', readonly=False)
    full_address = fields.Text(string="Full Address", compute="_compute_full_address")
    current_loans = fields.Integer(string='Current Loans', compute='_compute_current_loans')
    max_loans = fields.Integer(string='Max Allowed Loans', default=5)
    membership_type = fields.Selection([
        ('regular', 'Regular'),
        ('student', 'Student'),
        ('senior', 'Senior Citizen'),
    ], string='Membership Type', default='regular')
    transaction_ids = fields.One2many(
        'library.transaction',  # related model
        'member_id',  # inverse field name
        string='Transactions'
    )
    expiry_notification_sent = fields.Boolean(default=False)
    expiry_warning_date = fields.Date(compute='_compute_expiry_warning_date', store=True)
    barcode = fields.Char(string="Barcode", required=True, unique=True)

    @api.model_create_multi
    def create(self, vals_list):
        if not isinstance(vals_list, list):
            vals_list = [vals_list]

        for vals in vals_list:
            if not vals.get('barcode'):
                vals['barcode'] = self.env['ir.sequence'].next_by_code(
                    'library.member.barcode') or f"MEM-{fields.Datetime.now().strftime('%Y%m%d%H%M%S')}"

        return super(LibraryMember, self).create(vals_list)

    @api.depends('street', 'street2', 'city', 'state_id', 'country_id', 'zip')
    def _compute_full_address(self):
        for rec in self:
            lines = filter(None, [
                rec.street,
                rec.street2,
                f"{rec.city}, {rec.state_id.name}" if rec.city and rec.state_id else rec.city or rec.state_id.name,
                f"{rec.country_id.name} - {rec.zip}" if rec.country_id or rec.zip else None
            ])
            rec.full_address = '\n'.join(lines)

    # Override name_get to display name + membership number
    def name_get(self):
        result = []
        for member in self:
            name = f"{member.partner_id.name} ({member.membership_number})"
            result.append((member.id, name))
        return result

    @api.model
    def _generate_membership_number(self):
        """Generate a unique membership number"""
        while True:
            # Example format: LIB-2023-0001
            year = fields.Date.today().year
            random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
            number = f"LIB-{year}-{random_str}"

            # Ensure uniqueness
            if not self.search_count([('membership_number', '=', number)]):
                return number

    @api.depends()
    def _compute_current_loans(self):
        for member in self:
            member.current_loans = self.env['library.transaction'].search_count([
                ('member_id', '=', member.id),
                ('state', '=', 'borrowed')
            ])

    @api.depends('membership_end')
    def _compute_expiry_warning_date(self):
        for member in self:
            if member.membership_end:
                member.expiry_warning_date = fields.Date.to_date(member.membership_end) - timedelta(days=30)
            else:
                member.expiry_warning_date = False


    def _cron_check_expiring_memberships(self):
        """ Scheduled action to check expiring memberships """
        today = fields.Date.today()
        warning_date = today + timedelta(days=30)

        expiring_members = self.search([
            ('membership_end', '<=', warning_date),
            ('expiry_notification_sent', '=', False),
            ('active', '=', True)
        ])

        for member in expiring_members:
            member._send_expiry_notification()
            member.expiry_notification_sent = True

    def _send_expiry_notification(self):
        """ Send notification about expiring membership """
        self.ensure_one()
        template = self.env.ref('alan_library_management.membership_expiry_email_template')
        template.send_mail(self.id, force_send=True)

        # Create activity for follow-up
        self.activity_schedule(
            'mail.mail_activity_data_todo',
            date_deadline=self.membership_end,
            summary=f'Membership Renewal - {self.partner_id.name}',
            note=f'Membership expires on {self.membership_end}',
            user_id=self.env.user.id
        )
        _logger.info(f"Sent expiry notification for member {self.id}")

    def open_renew_wizard(self):
        """ Open the membership renewal wizard """
        return {
            'name': ('Renew Membership'),
            'type': 'ir.actions.act_window',
            'res_model': 'library.member.renew.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_partner_id': self.partner_id.id},
        }

    def renew_membership(self, renewal_days):
        """ Renew membership and reset notification flag """
        self.ensure_one()
        if not self.membership_end or fields.Date.today() > fields.Date.to_date(self.membership_end):
            self.membership_end = fields.Date.today() + timedelta(days=renewal_days)
        else:
            self.membership_end = fields.Date.to_date(self.membership_end) + timedelta(days=renewal_days)
        self.expiry_notification_sent = False
        self.message_post(body=f"Membership renewed for {renewal_days} days")

    def generate_qr_code(self):
        for record in self:
            qr = qrcode.QRCode(box_size=2, border=2)
            qr.add_data(record.name or 'Library Member')
            qr.make(fit=True)
            img = qr.make_image(fill='black', back_color='white')
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue())
            return img_str.decode()
