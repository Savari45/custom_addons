from odoo import models, fields, api, _
from datetime import datetime


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    expiry_date = fields.Char(string="Expiry", compute='get_lot_date')
    lot_ids = fields.Many2many('stock.lot', string='Serial Numbers', compute='get_lot_date')

    @api.onchange('invoice_date')
    def get_lot_date(self):
        for rec in self:
            lots = rec.sale_line_ids.move_ids.lot_ids or rec.purchase_line_id.move_ids.lot_ids
            date_list = []
            if rec.sale_line_ids or rec.purchase_line_id and lots:
                rec.lot_ids = lots
                for lot in lots:
                    if lot.expiration_date:  # Ensure expiration_date is not False
                        date_list.append(lot.expiration_date.strftime("%m/%Y"))
                rec.expiry_date = ", ".join(date_list) if date_list else ""
            else:
                rec.lot_ids = [(5, 0, 0)]
                rec.expiry_date = ""

