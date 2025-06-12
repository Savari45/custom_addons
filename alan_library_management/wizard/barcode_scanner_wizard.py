from odoo import models, fields, api
from odoo.exceptions import UserError


class BarcodeScannerWizard(models.TransientModel):
    _name = 'library.barcode.scanner.wizard'
    _description = 'Barcode Scanner Wizard'

    transaction_id = fields.Many2one('library.transaction', required=True)
    scan_type = fields.Selection([
        ('book', 'Book'),
        ('member', 'Member'),
    ], string='Scan Type', required=True)
    barcode = fields.Char(string='Barcode')

    def process_barcode(self):
        self.ensure_one()
        if not self.barcode:
            raise UserError("Please enter or scan a barcode")

        result = self.transaction_id.process_barcode(self.barcode, self.scan_type)

        if result['success']:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Success',
                    'message': result['message'],
                    'sticky': False,
                    'type': 'success',
                    'next': {'type': 'ir.actions.act_window_close'},
                }
            }
        else:
            raise UserError(result['message'])