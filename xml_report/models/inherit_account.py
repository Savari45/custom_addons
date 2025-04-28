from odoo import models, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_open_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Account Move Wizard',
            'res_model': 'generate.xml.report',
            'view_mode': 'form',
            'target': 'new',
        }
