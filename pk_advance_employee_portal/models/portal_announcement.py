from odoo import models, fields, api

class PortalAnnouncement(models.Model):
    _name = 'portal.announcement'
    _description = 'Portal Announcement'

    name = fields.Char(string='Title', required=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    description = fields.Text(string='Description', required=True)
    department_id = fields.Many2one('hr.department', string='Department', help="Department-specific announcements.")
    posted_by = fields.Many2one('res.users', string='Posted By', default=lambda self: self.env.user)
    post_date = fields.Datetime(string='Posted On', default=fields.Datetime.now)
    image_att = fields.Binary(string="Attachment",  attachment=True)

    # is_company_wide = fields.Boolean(string='Company-wide Announcement', default=True)
    # is_department_specific = fields.Boolean(string='Department-specific', default=False)

