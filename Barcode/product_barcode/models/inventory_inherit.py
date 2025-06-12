# models/stock_picking.py
from odoo import models, fields, api
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit = 'stock.picking'


    all_barcodes_present = fields.Boolean(
        string="All Move Barcodes Scanned",
        compute="_compute_all_barcodes",
        store=True,
    )

    @api.depends('move_ids.barcode')
    def _compute_all_barcodes(self):
        for pick in self:
            # True only if there is at least one move and every move.barcode is non-empty
            moves = pick.move_ids
            pick.all_barcodes_present = bool(moves) and all(
                bool(move.barcode) for move in moves
            )

    def button_validate(self):
        # server-side guard
        for pick in self:
            missing = pick.move_ids.filtered(lambda m: not m.barcode)
            if missing:
                raise UserError(
                    "Cannot validate: please scan or enter a barcode on every move."
                )
        return super().button_validate()


from odoo import models, fields

class StockMove(models.Model):
    _inherit = 'stock.move'

    barcode = fields.Char(string="Barcode")
