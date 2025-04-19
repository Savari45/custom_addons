from odoo import models, fields

class WhatsAppBotSession(models.Model):
    _name = 'whatsapp.bot.session'
    _description = 'WhatsApp Bot Session'

    phone = fields.Char(string="Customer Phone", required=True, unique=True)
    state = fields.Char(string="User State", default="new")
    cart = fields.Text(string="Cart", default="")
