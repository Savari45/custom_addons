# models/res_users.py

from odoo import models, fields,api

class ResUsers(models.Model):
    _inherit = 'res.users'

    can_view_encryption = fields.Boolean(string="Can View Encryption Reports")

