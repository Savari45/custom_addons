# -*- coding: utf-8 -*-
from odoo import api, models


class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.multi
    def get_invoice_number(self):
        self.ensure_one ()
        return self.invoice_id.number
