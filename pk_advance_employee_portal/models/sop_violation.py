# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SopViolationType(models.Model):
    _name = 'sop.violation.type'
    _description = 'sop violation'

    name = fields.Char(required=True)



class SopViolation(models.Model):
    _name = 'sop.violation'
    _description = 'sop violation'

    # violation_type_id = fields.Many2one(string="Violation Type", required=True)
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    violation_type = fields.Selection([
        ('late_arrival', 'Late Arrival'),
        ('excessive_break', 'Excessive Break'),
        ('fine', 'Fine'),
    ], string='Violation Type', required=True)
    date_violation = fields.Datetime(string='Violation Date', required=True)
    violation_reason = fields.Text(string='Reason for Violation', required=True)
    fine_amount = fields.Float(string='Fine Amount')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('resolved', 'Resolved'),
    ], string='Status', default='draft', required=True)

    # Automatically fill employee based on current user in portal
    @api.model
    def create(self, vals):
        if not vals.get('employee_id'):
            employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            if employee:
                vals['employee_id'] = employee.id
        return super(SopViolation, self).create(vals)

