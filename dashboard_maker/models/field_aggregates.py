# -*- coding: utf-8 -*-
from odoo import fields, models


FIELD_TYPES = [(key, key) for key in sorted(fields.Field.by_type)]


class FieldsAggregates(models.Model):
    _name = 'fields.aggregates'
    _description = 'Dashboard Maker Field Aggregates'
    _rec_name = 'aggregate_value'

    field_type = fields.Selection(selection=FIELD_TYPES, string='Field Type', required=True)
    aggregate_value = fields.Selection([
        ('sum', 'Sum'),
        ('avg', 'Average'),
        ('max', 'Maximum'),
        ('min', 'Minimum'),
        ('count', 'Count'),
        ('count_distinct', 'Unique Count'),
        ('array_agg', 'Values Array'),
    ], string="Aggregate")
