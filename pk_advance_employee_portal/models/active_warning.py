# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ActiveWarning(models.Model):
    _name = 'active.warning'
    _description = 'active warning'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    # warning_type = fields.Selection([
    #     ('late_arrival', 'Late Arrival'),
    #     ('excessive_break', 'Excessive Break'),
    #     ('fine', 'Fine'),
    # ], string='Violation Type', required=True)
    warning = fields.Text(string='Warning', required=True)
    warning_date = fields.Datetime(string='Warning Date', required=True)
    warning_reason = fields.Text(string='Warning Reason', required=True)
    potential_con = fields.Text(string='Potential Consequences', required=True)
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
        return super(ActiveWarning, self).create(vals)

