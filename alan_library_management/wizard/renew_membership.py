from odoo import models, fields, api

class MembershipRenewalWizard(models.TransientModel):
    _name = 'library.member.renew.wizard'
    _description = 'Membership Renewal Wizard'

    partner_id = fields.Many2one('res.partner', string='Name', required=True, readonly=False)
    duration = fields.Selection([
        ('30', '1 Month'),
        ('90', '3 Months'),
        ('180', '6 Months'),
        ('365', '1 Year')
    ], string="Renewal Duration", required=True, default='30')

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        if self.env.context.get('active_id'):
            member = self.env['library.member'].browse(self.env.context['active_id'])
            res['partner_id'] = member.partner_id.id
        return res

    def action_renew(self):
        member = self.env['library.member'].search([('partner_id', '=', self.partner_id.id)], limit=1)
        if member:
            member.renew_membership(int(self.duration))
        return {'type': 'ir.actions.act_window_close'}