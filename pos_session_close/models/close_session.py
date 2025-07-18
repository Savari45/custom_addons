# Inherit the pos.session model
from odoo import models, api, _
from odoo.exceptions import UserError

class PosSession(models.Model):
    _inherit = 'pos.session'

    def action_pos_session_closing_control(self):
        print("kkkkkkkkkkkkkkkkkkkkkkk")
        for session in self:
            print("session",session)
            if session.cash_register_balance_end_real == 0:
                raise UserError(_("Cash Out must be completed before closing the session."))

        return super(PosSession, self).action_pos_session_closing_control()
