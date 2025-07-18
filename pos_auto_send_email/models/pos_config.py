# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by CandidRoot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class PosConfig(models.Model):
    _inherit = 'pos.config'

    send_auto_email = fields.Boolean(string="Employees with access",
        help='Click to send auto email while validation of order.')
    