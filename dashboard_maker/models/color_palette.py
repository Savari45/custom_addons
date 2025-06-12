# -*- coding: utf-8 -*-
from odoo import fields, models


class ColorPalette(models.Model):
    _name = 'color.palette'
    _description = 'Dashboard Maker Color Palette'

    name = fields.Char(string="Name")
    colors_ids = fields.One2many('color.palette.line', 'color_palette_id',string="Colors")



class ColorPaletteLines(models.Model):
    _name = 'color.palette.line'
    _description = 'Dashboard Maker Color Palette Lines'

    name = fields.Char(string="Name")
    color_palette_id = fields.Many2one('color.palette',string="Color Palette", ondelete='cascade')
    sequence = fields.Integer(string="Sequence")
