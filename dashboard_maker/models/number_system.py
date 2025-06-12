# -*- coding: utf-8 -*-
from odoo import fields, models


class NumberSystem(models.Model):
    _name = 'number.system'
    _description = 'Dashboard Maker Number System'

    name = fields.Char(string="Number system name")
    line_ids = fields.One2many('number.system.line','number_system_id')


class NumberSystemLine(models.Model):
    _name = 'number.system.line'
    _description = 'Dashboard Maker Number System Lines'

    no_of_digits = fields.Integer(string="No.of digits")
    display_notation = fields.Char(string="Display string")
    number_system_id = fields.Many2one('number.system', string="Number system", ondelete='cascade')
