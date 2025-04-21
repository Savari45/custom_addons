from odoo import models, fields, api


class Teacher(models.Model):
    _name = 'school.teacher'
    _description = 'Teacher Record'

    name = fields.Char(string="Full Name", required=True)
    qualification = fields.Text(string="Qualification")
    subject_ids = fields.Many2many('school.subject', string="Subjects")
    contact_no = fields.Char(string="Contact Number")
    email = fields.Char(string="Email")
    joining_date = fields.Date(string="Joining Date")
