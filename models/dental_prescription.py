# -*- coding: utf-8 -*-
################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class DentalPrescription(models.Model):
    """Prescription of patient from the dental clinic"""
    _name = 'dental.prescription'
    _description = "Dental Prescription"
    _inherit = ['mail.thread']
    _rec_name = "sequence_no"

    sequence_no = fields.Char(string='Sequence No', required=True,
                              readonly=True, default=lambda self: _('New'),
                              help="Sequence number of the dental prescription")
    appointment_ids = fields.Many2many('dental.appointment',
                                       string="Appointment",
                                       compute="_compute_appointment_ids",
                                       help="All appointments created")
    appointment_id = fields.Many2one('dental.appointment',
                                     string="Appointment",
                                     domain="[('id','in',appointment_ids)]",
                                     required=True,
                                     help="All appointments created")
    patient_id = fields.Many2one(related="appointment_id.patient_id",
                                 string="Patient",
                                 required=True,
                                 help="name of the patient")
    # token_no = fields.Integer(related="appointment_id.token_no",
    #                           string="Token Number",
    #                           help="Token number of the patient")
    treatment_id = fields.Many2one('dental.treatment',
                                   string="Treatment",
                                   help="Name of the treatment done for patient")
    cost = fields.Float(related="treatment_id.cost",
                        string="Treatment Cost",
                        help="Cost of treatment")
    currency_id = fields.Many2one('res.currency', 'Currency',
                                  default=lambda self: self.env.user.company_id.currency_id,
                                  required=True,
                                  help="To add the currency type in cost")
    prescribed_doctor_id = fields.Many2one(related="appointment_id.dentist_id",
                                           string='Prescribed Doctor',
                                           required=True,
                                           help="Doctor who is prescribed")
    prescription_date = fields.Date(default=fields.date.today(),
                                    string='Prescription Date',
                                    required=True,
                                    help="Date of the prescription")
    state = fields.Selection([('new', 'New'),
                              ('done', 'Prescribed'),
                              ('invoiced', 'Invoiced')],
                             default="new",
                             string="state",
                             help="state of the appointment")
    medicine_ids = fields.One2many('dental.prescription_lines',
                                   'prescription_id',
                                   string="Medicine",
                                   help="medicines")
    invoice_data_id = fields.Many2one(comodel_name="account.move", string="Invoice Data",
                                      help="Invoice Data")
    selected_teeth = fields.Char(string="Selected Teeth",help="Selected Teeth")
    referred_dentist_id = fields.Many2one(
        'hr.employee', string='Referred Dentist',
        domain="[('is_dentist', '=', True)]",
        help="Select a different dentist if referring the patient"
    )
    next_appointment_date = fields.Date(
        string="Next Appointment Date",
        help="Date for the next appointment"
    )
    # grand_total = fields.Float(compute="_compute_grand_total",
    #                            string="Grand Total",
    #                            help="Get the grand total amount")

    @api.model_create_multi
    def create(self, vals_list):
        """Ensure the next appointment is updated/created when a prescription is created."""
        records = super(DentalPrescription, self).create(vals_list)
        for record in records:
            record._update_or_create_appointment()
        return records

    def write(self, vals):
        """Ensure the next appointment is updated when a prescription is modified."""
        res = super(DentalPrescription, self).write(vals)
        if 'next_appointment_date' in vals or 'referred_dentist_id' in vals:
            for record in self:
                record._update_or_create_appointment()
        return res

    def _update_or_create_appointment(self):
        """Creates a new appointment instead of modifying the current one."""
        if not self.next_appointment_date or not self.patient_id:
            return  # Skip if no next appointment date is given

        assigned_dentist = self.referred_dentist_id or self.prescribed_doctor_id
        if not assigned_dentist:
            return  # Skip if no doctor is assigned

        today_appointment = self.env['dental.appointment'].search([
            ('patient_id', '=', self.patient_id.id),
            ('appointment_date', '=', fields.Date.today()),
            ('state', '!=', 'done')
        ], limit=1)

        # Ensure that today's appointment is not modified
        if today_appointment:
            # Create a new appointment for the next visit
            self.env['dental.appointment'].create({
                'patient_id': self.patient_id.id,
                'appointment_date': self.next_appointment_date,
                'dentist_id': assigned_dentist.id,
                'state': 'draft',  # Set as draft since it's a future appointment
            })
        else:
            # If no active appointment exists today, update or create as usual
            upcoming_appointment = self.env['dental.appointment'].search([
                ('patient_id', '=', self.patient_id.id),
                ('appointment_date', '>', fields.Date.today()),
                ('state', '!=', 'done')
            ], limit=1, order="appointment_date asc")

            if upcoming_appointment:
                upcoming_appointment.write({
                    'appointment_date': self.next_appointment_date,
                    'dentist_id': assigned_dentist.id
                })
            else:
                # Create a new future appointment
                self.env['dental.appointment'].create({
                    'patient_id': self.patient_id.id,
                    'appointment_date': self.next_appointment_date,
                    'dentist_id': assigned_dentist.id,
                    'state': 'draft',
                })

    @api.depends('appointment_id')
    def _compute_appointment_ids(self):
        """Computes and assigns the `appointment_ids` field for each record.
        This method searches for all `dental.appointment` records that have
        a state of `new` and a date equal to today's date. It then updates
        the `appointment_ids` field of each `DentalPrescription` record
        with the IDs of these found appointments."""
        for rec in self:
            rec.appointment_ids = self.env['dental.appointment'].search(
                [('state', '=', 'confirmed'), ('appointment_date', '=', fields.Date.today())]).ids

    def action_prescribed(self):
        """Marks the prescription and its associated appointment as `done`.
        This method updates the state of both the DentalPrescription instance
        and its linked dental.appointment instance to `done`, indicating that
        the prescription has been finalized and the appointment has been completed.
        """
        self.state = 'done'
        self.appointment_id.state = 'done'

    def create_invoice(self):
        """Create an invoice based on the patient invoice and manage stock moves for medicines."""
        self.ensure_one()
        medicine_moves = []
        for rec in self.medicine_ids:
            product_id = self.env['product.product'].search([
                ('product_tmpl_id', '=', rec.medicament_id.id)], limit=1)
            if product_id and product_id.type == 'consu':  # Only stockable products
                medicine_moves.append({
                    'product_id': product_id,
                    'quantity': rec.quantity,
                })

        invoice_vals = {
            'move_type': 'out_invoice',
            'partner_id': self.patient_id.id,
            'state': 'draft',
            'invoice_line_ids': [
                fields.Command.create({
                    'name': self.treatment_id.name,
                    'quantity': 1,
                    'price_unit': self.cost,
                })
            ]
        }
        invoice = self.env['account.move'].create(invoice_vals)

        for rec in self.medicine_ids:
            product_id = self.env['product.product'].search([
                ('product_tmpl_id', '=', rec.medicament_id.id)], limit=1)
            if product_id:
                invoice.write({
                    'invoice_line_ids': [(0, 0, {
                        'product_id': product_id.id,
                        'name': rec.display_name,
                        'quantity': rec.quantity,
                        'price_unit': rec.price,
                    })]
                })

        if medicine_moves:
            warehouse = self.env['stock.warehouse'].search([('company_id', '=', self.env.company.id)], limit=1)
            if not warehouse:
                raise UserError(_('No warehouse found for the company. Please configure a warehouse.'))
            source_location = warehouse.lot_stock_id  # Clinic's stock location
            customer_location = self.env.ref('stock.stock_location_customers')  # Customer location

            for move in medicine_moves:
                self.env['stock.move'].create({
                    'name': f'Prescription {self.sequence_no}',
                    'product_id': move['product_id'].id,
                    'product_uom_qty': move['quantity'],
                    'quantity': move['quantity'],
                    'product_uom': move['product_id'].uom_id.id,
                    'location_id': source_location.id,
                    'location_dest_id': customer_location.id,
                    'state': 'done',
                })

        self.invoice_data_id = invoice.id
        self.state = 'invoiced'

        return {
            'name': _('Customer Invoice'),
            'view_mode': 'form',
            'view_id': self.env.ref('account.view_move_form').id,
            'res_model': 'account.move',
            'context': "{'move_type':'out_invoice'}",
            'type': 'ir.actions.act_window',
            'res_id': self.invoice_data_id.id,
        }

    def action_view_invoice(self):
        """Invoice view"""
        return {
            'name': _('Customer Invoice'),
            'view_mode': 'form',
            'view_id': self.env.ref('account.view_move_form').id,
            'res_model': 'account.move',
            'context': "{'move_type':'out_invoice'}",
            'type': 'ir.actions.act_window',
            'res_id': self.invoice_data_id.id,
        }
    def action_print_prescription(self):
        return self.env.ref('smile_hospital.report_pdf_dental_prescription').report_action(self)




class DentalPrescriptionLines(models.Model):
    """Prescription lines of the dental clinic prescription"""
    _name = 'dental.prescription_lines'
    _description = "Dental Prescriptions Lines"
    _rec_name = "medicament_id"

    medicament_id = fields.Many2one('product.template',
                                    domain="[('is_medicine', '=', True)]",
                                    string="Medicament",
                                    help="Name of the medicine")
    generic_name = fields.Char(string="Generic Name",
                               related="medicament_id.generic_name",
                               help="Generic name of the medicament")
    dosage_strength = fields.Integer(string="Dosage Strength",
                                     related="medicament_id.dosage_strength",
                                     help="Dosage strength of medicament")
    medicament_form = fields.Selection([('tablet', 'Tablets'),
                             ('capsule', 'Capsules'),
                             ('liquid', 'Liquid'),
                             ('injection', 'Injections')],
                            string="Medicament Form",
                            required=True,
                            help="Add the form of the medicine")
    quantity = fields.Integer(string="Quantity",
                              required=True,
                              help="Quantity of medicine")
    # frequency_id = fields.Many2one('medicine.frequency',
    #                                string="Frequency",
    #                                required=True,
    #                                help="Frequency of medicine")
    price = fields.Float(related='medicament_id.list_price',
                          string="Price",
                          help="Cost of medicine")
    prescription_id = fields.Many2one('dental.prescription',
                                      help="Relate the model with dental_prescription")
    morning = fields.Boolean(string="Morning")
    noon = fields.Boolean(string="After Noon")
    night = fields.Boolean(string="Night")
    medicine_take = fields.Selection([
        ('before', 'Before Food'),
        ('after', 'After Food')
    ], string='Medicine Take',default='after')
    days = fields.Float(string='Days')




