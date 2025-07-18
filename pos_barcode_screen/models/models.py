# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
# 
#################################################################################
from odoo import fields, models

class PosConfig(models.Model):
	_inherit = 'pos.config'

	show_barcode_screen = fields.Boolean(string="Show Barcode Screen", default=True)

class ResConfigSettings(models.TransientModel):
	_inherit = 'res.config.settings'

	pos_show_barcode_screen = fields.Boolean(related='pos_config_id.show_barcode_screen', readonly=False)