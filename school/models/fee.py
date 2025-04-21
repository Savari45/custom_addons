from odoo import models, fields

class FeePayment(models.Model):
    _name = 'school.fee.payment'
    _description = 'Fee Payment'
    _order = 'payment_date desc'

    admission_no = fields.Many2one('school.student', string="Admission No", required=True)
    academic_year = fields.Char(string="Academic Year", required=True)
    amount_paid = fields.Float(string="Amount Paid", required=True)
    payment_date = fields.Date(string="Payment Date", required=True, default=fields.Date.today)
    payment_mode = fields.Selection(
        [('cash', 'Cash'), ('online', 'Online'), ('cheque', 'Cheque')],
        string="Payment Mode", required=True
    )
    note = fields.Text(string="Remarks / Description")
