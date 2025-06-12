# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import ast
import re
from odoo.tools.safe_eval import safe_eval
import json
from odoo.exceptions import AccessError
from odoo.fields import Command
from odoo.osv import expression

sorter_align = {
    'binary': 'string',
    'boolean': 'string',
    'char': 'string',
    'date': 'string',
    'datetime': 'string',
    'float': 'number',
    'html': 'string',
    'integer': 'number',
    'json': 'string',
    'many2one': 'string',
    'many2many': 'string',
    'monetary': 'number',
    'selection': 'string',
    'text': 'string',
}
value_formatters = {
    'binary': 'image',
    'boolean': 'plaintext',
    'char': 'plaintext',
    'date': 'plaintext',
    'datetime': 'plaintext',
    'float': 'number',
    'html': 'html',
    'integer': 'number',
    'json': 'json',
    'many2one': 'plaintext',
    'many2many': 'plaintext',
    'monetary': 'number',
    'selection': 'plaintext',
    'text': 'textarea',
}


class DashboardCharts(models.Model):
    _name = 'dashboard.chart'
    _description = 'Dashboard charts'
    _order = 'grid_y, grid_x'

    name = fields.Char(string="Item Title", translate=True)
    dashboard_id = fields.Many2one('dashboard.dashboard', string="Show under dashboard")
    type = fields.Selection([('card', 'Card'), ('list', 'List'),
                             ('bar', 'Bar'), ('line', 'Line'), ('h_bar', 'Horizontal Bar'), ('area', 'Area'),
                             ('pie', 'Pie'), ('h_pie', 'Half Pie'), ('doughnut', 'Doughnut'), ('h_doughnut', 'Half Doughnut'),
                             ('scatter', 'Scatter'), ('funnel', 'Funnel')
                             ], string="Item Type", default='card')

    data_filter_ids = fields.One2many('groups.data.filter', 'chart_id', string="Data filters")
    filter_mapping_ids = fields.One2many('filter.mapping', 'chart_id', string="Filters mapping")

    model_id = fields.Many2one('ir.model', string='Model name', domain="[('transient','=',False)]")
    model_name = fields.Char(related='model_id.model', string="Model Name")

    display_field_ids = fields.One2many('field.display', 'chart_id', string="Fields to display data")

    display_field_id = fields.Many2one('ir.model.fields', domain="[('model_id','=',model_id), ('store','=',True), ('ttype', 'not in', ['binary', 'one2many', 'many2many'])]", string="Field to display data")
    display_field_type = fields.Selection(related='display_field_id.ttype', string="Display Field Type")
    display_field_agg = fields.Many2one('fields.aggregates', domain="[('field_type','=',display_field_type)]", string="Aggregation")

    list_view_id = fields.Many2one('ir.ui.view', string="List view", domain="[('model','=',model_name), ('type','=','list')]")
    form_view_id = fields.Many2one('ir.ui.view', string="Form view", domain="[('model','=',model_name), ('type','=','form')]")

    group_field_ids = fields.One2many('fields.selection', 'chart_id', 'Group by Fields')

    group_field_id = fields.Many2one('ir.model.fields', domain="[('model_id','=',model_id), ('store','=',True), ('ttype', 'not in', ['binary', 'one2many'])]", string="Group By")
    group_field_type = fields.Selection(related='group_field_id.ttype', string="Group Field Type")
    group_date_aggregates = fields.Selection([('day', 'Day'), ('week', 'Week'), ('month', 'Month'), ('quarter', 'Quarter'), ('year', 'Year')], string="Group by date aggregation")

    sub_group_field_id = fields.Many2one('ir.model.fields', domain="[('model_id','=',model_id), ('store','=',True), ('ttype', 'not in', ['binary', 'one2many'])]", string="Sub Group By")
    sub_group_field_type = fields.Selection(related='sub_group_field_id.ttype', string="Sub Group Field Type")
    sub_group_date_aggregates = fields.Selection([('day', 'Day'), ('week', 'Week'), ('month', 'Month'), ('quarter', 'Quarter'), ('year', 'Year')], string="Sub group by date aggregation")

    fields_stacked = fields.Boolean(string="Display fields data as stacked")
    groups_stacked = fields.Boolean(string="Display group by data as stacked")

    number_system_id = fields.Many2one('number.system', string="Number Abbreviations")
    color_palette_id = fields.Many2one('color.palette', string="Color Palette")

    enable_zoom = fields.Boolean(string="Enable chart Zooming", default=False)

    # data for grid position
    grid_x = fields.Integer(string="Grid x position", default=0)
    grid_y = fields.Integer(string="Grid y position")
    grid_w = fields.Integer(string="Grid width", default=10)
    grid_h = fields.Integer(string="Grid height", default=10)
    grid_mobile_h = fields.Integer(string="Grid mobile height", default=10)

    card_format = fields.Selection([('format_1', 'Format 1'), ('format_2', 'Format 2'), ('format_3', 'Format 3'), ('format_4', 'Format 4'),
                                    ('format_5', 'Format 5'), ('format_6', 'Format 6'), ('format_7', 'Format 7'), ('format_8', 'Format 8'),
                                    ('format_9', 'Format 9'), ('format_10', 'Format 10')], string="Card Format")

    override_custom_datefilter = fields.Boolean(string="Override default date filter")

    preview_data = fields.Text(string="Preview data", compute="compute_preview_data")

    bg_color = fields.Char(string="Background Color")
    title_color = fields.Char(string="Title Color")
    value_color = fields.Char(string="Value Color")
    border_color = fields.Char(string="Border Color")

    sort_field_ids = fields.One2many('sort.field', 'chart_id', string="Sort fields")
    records_limit = fields.Integer(string="Limit max records")
    data_limit = fields.Integer(string="Records limit per page", default=0)

    datetime_filter_field = fields.Many2one('ir.model.fields', string="Apply date filter on field",
                                            domain="[('model_id', '=', model_id), ('store','=',True), ('ttype', 'in', ['date', 'datetime'])]")
    date_filter_default = fields.Many2one('date.filters', string="Default Date filter")
    custom_datetime_start = fields.Datetime(string="Start date")
    custom_datetime_end = fields.Datetime(string="End date")

    smooth_line = fields.Boolean(string="Smooth line")
    step_line = fields.Boolean(string="Step line")
    step_position = fields.Selection([('start', 'Start'), ('middle', 'Middle'), ('end', 'End')], string="Step position")

    list_grouped = fields.Boolean(compute="_check_list_grouped")

    use_sql = fields.Boolean(string="Use SQL Query")
    input_query = fields.Text(string="Query")
    sql_bar_type = fields.Selection([('grouped', 'Grouped'), ('sub_grouped', 'Grouped + Sub-Grouped')])

    display_data_value = fields.Boolean(string="Display Data Value")
    pie_label_format = fields.Selection([('name', "Name"), ('value', "Value"), ('per', 'Percentage'), ('name_value', 'Name+Value'), ('name_per', 'Name+Percentage')], string="Label Format")
    show_records = fields.Boolean(string="Show records on click", default=True)

    scatter_x = fields.Many2one('ir.model.fields', string="Scatter X", domain="[('model_id', '=', model_id), ('store','=',True), ('ttype', 'in', ['float', 'integer', 'monetary'])]")
    scatter_y = fields.Many2one('ir.model.fields', string="Scatter Y", domain="[('model_id', '=', model_id), ('store','=',True), ('ttype', 'in', ['float', 'integer', 'monetary'])]")
    scatter_y_type = fields.Selection(related='scatter_y.ttype', string="Scatter Y Type")
    scatter_y_agg = fields.Many2one('fields.aggregates', domain="[('field_type','=',scatter_y_type)]", string="Scatter Y Aggregation")

    def copy_data(self, default=None):
        default = dict(default or {})
        vals_list = super().copy_data(default=default)
        for chart, vals in zip(self, vals_list):
            vals['data_filter_ids'] = [
                Command.create(data_filter_vals)
                for data_filter_vals in chart.data_filter_ids.copy_data()
            ]
            vals['filter_mapping_ids'] = [
                Command.create(filter_mapping_vals)
                for filter_mapping_vals in chart.filter_mapping_ids.copy_data()
            ]
            vals['display_field_ids'] = [
                Command.create(display_field_vals)
                for display_field_vals in chart.display_field_ids.copy_data()
            ]
            vals['group_field_ids'] = [
                Command.create(group_field_vals)
                for group_field_vals in chart.group_field_ids.copy_data()
            ]
            vals['sort_field_ids'] = [
                Command.create(sort_field_vals)
                for sort_field_vals in chart.sort_field_ids.copy_data()
            ]
        return vals_list

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            pass
        return records

    @api.onchange('model_id')
    def _onchange_model_id(self):
        for rec in self:
            rec.write({
                'display_field_id': False,
                'scatter_x': False,
                'scatter_y': False,
                'group_field_id': False,
                'sub_group_field_id': False,
                'datetime_filter_field': False,
                'data_filter_ids': [(2, data_filter.id, 0) for data_filter in rec.data_filter_ids],
                'filter_mapping_ids': [(2, filter_map.id, 0) for filter_map in rec.filter_mapping_ids],
                'display_field_ids': [(2, display_field.id, 0) for display_field in rec.display_field_ids],
                'group_field_ids': [(2, group_field.id, 0) for group_field in rec.group_field_ids],
                'sort_field_ids': [(2, sort_field.id, 0) for sort_field in rec.sort_field_ids],
            })

    @api.depends('group_field_ids')
    def _check_list_grouped(self):
        for rec in self:
            rec.list_grouped = rec.type == 'list' and not rec.group_field_ids

    @api.onchange('type')
    def onchange_type(self):
        for rec in self:
            rec.data_limit = 40 if rec.type == 'list' else False
            if rec.type == 'card':
                rec.card_format = 'format_1'
            else:
                rec.card_format = False
            rec.color_palette_id = self.env.ref('dashboard_maker.default_colors').id

    @api.onchange('type', 'display_field_id', 'display_field_agg', 'model_id', 'name', 'card_format', 'bg_color', 'title_color', 'value_color', 'border_color', 'number_system_id',
                  'display_field_ids', 'group_field_ids', 'data_limit', 'records_limit', 'sort_field_ids', 'datetime_filter_field', 'date_filter_default', 'custom_datetime_start', 'custom_datetime_end',
                  'group_field_id','pie_label_format', 'display_data_value', 'data_filter_ids', 'group_date_aggregates', 'sub_group_field_id', 'sub_group_date_aggregates',
                  'fields_stacked', 'groups_stacked', 'color_palette_id', 'smooth_line', 'step_line', 'icon_color', 'input_query', 'scatter_x', 'scatter_y', 'scatter_y_agg')
    def compute_preview_data(self):
        for rec in self:
            chart_data = rec.get_charts_data()
            for data in chart_data.values():
                if 'id' in data:
                    del data['id']
                rec.preview_data = json.dumps(data, default=str)
                break

    def chart_number_system_format(self):
        if not (self.number_system_id and self.number_system_id.line_ids):
            return []

        return [
            (line.no_of_digits, line.display_notation)
            for line in sorted(self.number_system_id.line_ids, key=lambda l: l.no_of_digits, reverse=True)
        ]

    def conditional_replace(self, domain_string, replacement):
        pattern = r'(?<!in",)\["(?![&|])'
        return re.sub(pattern, replacement, domain_string)

    def process_filter_domain(self, filter_domain, model_name):
        final_domain = []
        for domain in filter_domain:
            temp_domain = []

            relevant_mappings = self.filter_mapping_ids.filtered(lambda x: x.chart_model_id.model == model_name and x.filter_id.model in domain)
            for mapping in relevant_mappings:
                domain_string = domain[mapping.filter_id.model]
                domain_condition = ['|'] * max(len(mapping.field_ids) - 1, 0)

                for field in mapping.field_ids:
                    replaced_domain = self.conditional_replace(domain_string, f'["{field.name}.')
                    domain_condition.extend(ast.literal_eval(replaced_domain))
                temp_domain.extend(domain_condition)

            if model_name in domain:
                temp_domain.extend(ast.literal_eval(domain[model_name]))
            final_domain.extend(temp_domain)

        return final_domain

    def get_default_domain(self, model_name):
        if not self.data_filter_ids:
            return []

        for filter in sorted(self.data_filter_ids.filtered(lambda l: l.model_id.model == model_name), key=lambda f: f.sequence):
            if not filter.group_ids:
                return safe_eval(filter.domain, dict(self.env.context), nocopy=True) if filter.domain else []
            groups = ",".join(filter.group_ids._ensure_xml_id().values())
            if self.env.user.has_groups(groups):
                return safe_eval(filter.domain, dict(self.env.context), nocopy=True) if filter.domain else []

        return []

    def get_datetime_domain(self, datetime_filter, date_filter_field, field_type):
        datetime_domain = []
        if not date_filter_field:
            return datetime_domain
        default_date_filter = self.date_filter_default
        custom_datetime_start = self.custom_datetime_start
        custom_datetime_end = self.custom_datetime_end
        if not date_filter_field:
            return datetime_domain

        start_date = False
        end_date = False
        if not self.override_custom_datefilter:
            if default_date_filter:
                if field_type == 'date':
                    start_date = default_date_filter.date_start
                    end_date = default_date_filter.date_end
                elif field_type == 'datetime':
                    start_date = default_date_filter.datetime_start
                    end_date = default_date_filter.datetime_end
            elif custom_datetime_start and custom_datetime_end:
                if field_type == 'date':
                    start_date = custom_datetime_start.strftime('%Y-%m-%d')
                    end_date = custom_datetime_end.strftime('%Y-%m-%d')
                elif field_type == 'datetime':
                    start_date = custom_datetime_start
                    end_date = custom_datetime_end
            elif datetime_filter['datetime_start']:
                if field_type == 'date':
                    start_date = datetime_filter['datetime_start']
                    end_date = datetime_filter['datetime_end']
                elif field_type == 'datetime':
                    start_date = datetime_filter['date_start']
                    end_date = datetime_filter['date_end']
        else:
            if datetime_filter['datetime_start']:
                if field_type == 'datetime':
                    start_date = datetime_filter['datetime_start']
                    end_date = datetime_filter['datetime_end']
                elif field_type == 'date':
                    start_date = datetime_filter['date_start']
                    end_date = datetime_filter['date_end']
            elif default_date_filter:
                if field_type == 'date':
                    start_date = default_date_filter.date_start
                    end_date = default_date_filter.date_end
                elif field_type == 'datetime':
                    start_date = default_date_filter.datetime_start
                    end_date = default_date_filter.datetime_end
            elif custom_datetime_start and custom_datetime_end:
                if field_type == 'date':
                    start_date = custom_datetime_start.strftime('%Y-%m-%d')
                    end_date = custom_datetime_end.strftime('%Y-%m-%d')
                elif field_type == 'datetime':
                    start_date = custom_datetime_start
                    end_date = custom_datetime_end

        if start_date and end_date:
            datetime_domain = ['&', (date_filter_field, '>=', start_date),
                                       (date_filter_field, '<=', end_date)]

        return datetime_domain

    def process_sort_order(self, all_fields):
        if not self.sort_field_ids:
            return ''
        order = []
        for order_field in sorted(self.sort_field_ids, key=lambda x: x.sequence):
            if order_field.field_id.id in all_fields:
                order.append(f"{all_fields[order_field.field_id.id]} {order_field.sort_type}")
        order = ", ".join(order)
        return order

    def get_pie_specific_options(self):
        options = {
            "tooltip": {
                "trigger": 'item',
            },
            "grid": {
                "left": '1%',
                "top": '4%',
                "right": '4%',
                "bottom": '3%',
                "containLabel": True
            },
            "color": self.get_chart_colors()
        }
        return options

    def get_scatter_specific_options(self):
        options = {
            "tooltip": {
                "trigger": 'item',
            },
            "grid": {
                "left": '1%',
                "top": '4%',
                "right": '4%',
                "bottom": '3%',
                "containLabel": True
            },
            "color": self.get_chart_colors()
        }
        return options

    def get_bar_line_specific_options(self):
        options = {
            "tooltip": {
                "trigger": 'axis',
                "axisPointer": {
                    "type": "shadow" if self.type in ['bar', 'h_bar'] else 'line'
                }
            },
            "dataZoom": {
                "type": 'inside',
                "disabled": not self.enable_zoom,
                "filterMode": "empty"
            },
            "grid": {
                "left": '1%',
                "top": '4%',
                "right": '4%',
                "bottom": '3%',
                "containLabel": True,
                "show": True
            },
            "color": self.get_chart_colors(),
        }
        return options

    def get_chart_colors(self):
        return [color.name for color in self.color_palette_id.colors_ids]

    @api.readonly
    def _get_card_sql_data(self, sql_query):
        if not sql_query:
            return {'is_error': True, 'error_log': "Please enter the query"}

        try:
            self.env.cr.execute(sql_query)
            result = self.env.cr.fetchone()
            data_value = round(result[0], 2) if result and result[0] is not None else 0
        except Exception as e:
            return {'is_error': True, 'error_log': str(e)}

        return {
            'card_format': self.card_format,
            'value': data_value,
            'bg_color': self.bg_color or '#fff',
            'title_color': self.title_color,
            'value_color': self.value_color,
            'border_color': self.border_color or '#ccc',
        }

    def _get_card_data(self, domain):
        if not self.model_id:
            return {'is_error': True, 'error_log': "Please select the model name"}
        if not self.display_field_id:
            return {'is_error': True, 'error_log': "Please select the field to display data"}
        if not self.display_field_agg:
            return {'is_error': True, 'error_log': "Please select the aggregation"}

        field_name = self.display_field_id.name
        field_agg = f"{field_name}:{self.display_field_agg.aggregate_value}"

        group_results = self.env[self.model_id.model].read_group(domain, [field_agg], [])[0]
        data_value = round(group_results.get(field_name, 0), 2)

        return {
            'card_format': self.card_format,
            'value': data_value,
            'domain': group_results.get('__domain', False),
            'bg_color': self.bg_color or '#fff',
            'title_color': self.title_color,
            'value_color': self.value_color,
            'border_color': self.border_color or '#ccc',
        }

    def get_list_sql_data(self, domain=(), offset=0, navigation=False):
        sql_query = self.process_sql_query(domain[0], domain[1])
        if not sql_query:
            return {'is_error': True, 'error_log': "Please enter the query"}

        if 'dm#offset' not in sql_query:
            return {'is_error': True, 'error_log': "Please mention the keyword 'dm#offset' in your query. We made it compulsory to improve the performance"}
        if 'dm#limit' not in sql_query:
            return {'is_error': True, 'error_log': "Please mention the keyword 'dm#limit' in your query. We made it compulsory to improve the performance"}

        offset += self.data_limit if navigation == 'next' else -self.data_limit if navigation == 'previous' else 0

        limit = self.data_limit if self.data_limit > 0 else 40
        if 0 < self.records_limit < offset + limit:
            limit = self.records_limit - offset

        sql_query = sql_query.replace('dm#offset', str(offset)).replace('dm#limit', str(limit + 1))

        try:
            self.env.cr.execute(sql_query)
            results = self.env.cr.dictfetchall()
        except Exception as e:
            return {'is_error': True, 'error_log': str(e)}

        pager_data = {'offset': offset}
        if self.records_limit:
            if offset + len(results) > self.records_limit:
                pager_data['is_last'] = True
                results = results[:-1]
            elif offset + len(results) == self.records_limit:
                pager_data['is_last'] = True
            else:
                pager_data['is_last'] = False
                results = results[:-1]
        else:
            if len(results) > limit:
                pager_data['is_last'] = False
                results = results[:-1]
            elif len(results) == limit:
                pager_data['is_last'] = True
            else:
                pager_data['is_last'] = True

        pager_data['limit'] = len(results)

        types_data = {
            '16': 'boolean', '23': 'integer', '1043': 'char', '25': 'text',
            '20': 'integer', '1700': 'float', '701': 'float', '1082': 'date', '1114': 'datetime'
        }

        fields_data = []
        field_types = {}
        fields_info = self.env.cr.description
        for field in fields_info:
            field_types[field[0]] = types_data.get(str(field[1]), 'char')
            fields_data.append(
                {'type': types_data.get(str(field[1]), 'char'), 'description': field[0], 'name': field[0]})

        return {
            'data': results,
            'is_grouped': False,
            'field_types': field_types,
            'fields_data': fields_data,
            'pager_data': pager_data,
            'list_domain': domain
        }

    def list_item_data(self, domain=(), offset=0, navigation=False):
        offset += self.data_limit if navigation == 'next' else -self.data_limit if navigation == 'previous' else 0

        if not self.model_id:
            return {'is_error': True, 'error_log': "Please select the model name"}
        if not self.display_field_ids:
            return {'is_error': True, 'error_log': "Please select the fields to display data"}
        if self.group_field_ids:
            for display_field in self.display_field_ids:
                if not display_field.field_aggregation_id:
                    return {'is_error': True,
                            'error_log': f"Please select the aggregation for the field: {display_field.name}"}

        group_by, fields_agg, fields_data, all_fields_data, field_types = [], [], [], {}, {}

        for field in self.group_field_ids.sorted('sequence'):
            if not field.field_id:
                continue
            field_name = field.field_id.name
            all_fields_data[field.field_id.id] = field_name
            field_types[field_name] = field.field_id.ttype if field.field_type not in ['date', 'datetime'] else None
            if field.field_type in ['date', 'datetime']:
                if not field.date_aggregates:
                    return {'is_error': True, 'error_log': "Please select the Date aggregation for date field"}
                field_name += f":{field.date_aggregates}"
            group_by.append(field_name)
            fields_data.append({'type': field.field_type, 'description': field.display_string, 'name': field_name})

        for field in self.display_field_ids.sorted('sequence'):
            if not field.field_id:
                continue
            base_field_name = field.field_id.name
            field_name = f"{base_field_name}_{field.field_aggregation_id.aggregate_value}" if field.field_aggregation_id and self.group_field_ids else base_field_name
            field_agg = f"{field_name}:{field.field_aggregation_id.aggregate_value}({base_field_name})" if field.field_aggregation_id and self.group_field_ids else field_name
            fields_agg.append(field_agg)
            all_fields_data[field.field_id.id] = field_name
            fields_data.append({'type': field.field_type, 'description': field.name, 'name': field_name})

            if field.field_type in ['float', 'integer', 'monetary'] or not (self.group_field_ids or (field.field_aggregation_id and self.group_field_ids)):
                field_types[field_name] = field.field_id.ttype

        order = self.process_sort_order(all_fields_data)
        limit = self.data_limit if self.data_limit else 40
        if self.records_limit and offset + limit > self.records_limit:
            limit = self.records_limit - offset

        if self.group_field_ids:
            results = self.env[self.model_id.model].read_group(domain, fields_agg, group_by, offset, limit + 1,
                                                               orderby=order, lazy=False)
        else:
            results = self.env[self.model_id.model].search_read(domain, fields_agg, offset, limit + 1, order=order)

        pager_data = {
            'offset': offset,
        }
        if self.records_limit:
            if offset + len(results) > self.records_limit:
                pager_data['is_last'] = True
                results = results[:-1]
            elif offset + len(results) == self.records_limit:
                pager_data['is_last'] = True
            else:
                pager_data['is_last'] = False
                results = results[:-1]
        else:
            if len(results) > limit:
                pager_data['is_last'] = False
                results = results[:-1]
            elif len(results) == limit:
                pager_data['is_last'] = True
            else:
                pager_data['is_last'] = True

        pager_data['limit'] = len(results)

        return {
            'data': results,
            'is_grouped': bool(self.group_field_ids),
            'field_types': field_types,
            'fields_data': fields_data,
            'pager_data': pager_data,
            'list_domain': domain,
        }

    @api.readonly
    def _get_bar_line_sql_data(self, sql_query):
        fields_data = {}
        if not sql_query:
            return {'is_error': True, 'error_log': "Please enter the query"}

        try:
            self.env.cr.execute(sql_query)
        except Exception as e:
            return {'is_error': True, 'error_log': e}
        results = self.env.cr.dictfetchall()
        fields_info = self.env.cr.description
        all_fields = [field[0] for field in fields_info]
        group_fields = all_fields[:2] if self.sql_bar_type=='sub_grouped' else [all_fields[0]]
        fields_list = all_fields[2:] if self.sql_bar_type=='sub_grouped' else all_fields[1:]

        for field in fields_list:
            fields_data[field] = field

        if self.sql_bar_type == 'grouped' and len(fields_list) == 1:
            chart_type = 'simple'
        elif len(fields_list) > 1 and self.fields_stacked and not self.groups_stacked:
            chart_type = 'field_stacked'
        elif self.sql_bar_type == 'grouped' and len(fields_list) > 1 and not self.fields_stacked:
            chart_type = 'field_grouped'
        elif self.sql_bar_type == 'sub_grouped' and len(fields_list) and self.groups_stacked and not self.fields_stacked:
            chart_type = 'group_stacked'
        elif self.sql_bar_type == 'sub_grouped' and len(fields_list) == 1 and not self.groups_stacked:
            chart_type = 'group_grouped'
        elif self.sql_bar_type == 'sub_grouped' and len(fields_list) > 1 and (not self.groups_stacked) and (not self.fields_stacked):
            chart_type = 'grouped_grouped'
        elif self.sql_bar_type == 'sub_grouped' and len(fields_list) > 1 and self.groups_stacked and self.fields_stacked:
            chart_type = 'stacked_stacked'
        else:
            chart_type = 'simple'

        if self.type == 'area':
            actual_type = 'line'
        elif self.type == 'h_bar':
            actual_type = 'bar'
        else:
            actual_type = self.type

        if chart_type == 'field_grouped' or chart_type == 'simple' or (chart_type == 'field_stacked' and len(group_fields)<=1):
            if chart_type == 'field_stacked':
                series = [{'type': actual_type, 'name': field, 'stack': group_fields[0]} for field in
                          fields_list]
            else:
                series = [{'type': actual_type, 'name': field} for field in fields_list]
            options = {
                "dataset": {
                    "dimensions": all_fields,
                    "source": results
                },
                "xAxis": [{
                    "type": 'category',
                    "axisLabel": {
                        "show": True,
                        "rotate": 50 if self.type != 'h_bar' else 0,
                        "width": 300,
                        "overflow": "truncate"
                    }
                }],
                "yAxis": {},
                "series": series
            }

            return {'options': options, 'data_domains': [], 'bar_type': chart_type,
                    'chart_basic_info': self.get_bar_line_specific_options()}

        elif chart_type == 'field_stacked' or chart_type == 'group_stacked' or chart_type == 'grouped_grouped' or chart_type == 'stacked_stacked' or chart_type == 'group_grouped':
            group_values = []
            sub_group_values = []

            for entry in results:
                if entry[group_fields[0]] not in group_values:
                    group_values.append(entry[group_fields[0]])
                if entry[group_fields[1]] not in sub_group_values:
                    sub_group_values.append(entry[group_fields[1]])

            series_data = []
            for sub_value in sub_group_values:
                for field in fields_list:
                    temp_list = []
                    for value in group_values:
                        data = [d[field] for d in results if
                                d[group_fields[0]] == value and d[group_fields[1]] == sub_value]
                        if data:
                            temp_list.append(data[0])
                        else:
                            temp_list.append(0)
                    temp_data = {
                        'name': sub_value + ", " + field,
                        'type': actual_type,
                        'data': temp_list
                    }
                    if chart_type == 'field_stacked':
                        temp_data['stack'] = sub_value
                    elif chart_type == 'group_stacked':
                        temp_data['stack'] = field
                    elif chart_type == 'stacked_stacked':
                        temp_data['stack'] = True
                    series_data.append(temp_data)

            options = {"xAxis": [{
                "type": 'category',
                "data": group_values,
                "axisLabel": {
                    "show": True,
                    "rotate": 50,
                    "width": 300,
                    "overflow": "truncate"
                }
            }],
                "yAxis": [
                    {
                        "type": 'value'
                    }
                ],
                "series": series_data
            }

            return {'options': options, 'chart_basic_info': self.get_bar_line_specific_options(),
                    'fields_count': len(fields_list), 'bar_type': chart_type,
                    'data_domains': [], 'sub_available': bool(self.sql_bar_type=='sub_grouped')}

        return {'is_error': True, 'error_log': "Something went wrong. Please check the chart configurations"}

    def _get_bar_line_data(self, chart_type, domain):

        if not self.model_id:
            return {'is_error': True, 'error_log': "Please select the model name"}
        if not self.group_field_id:
            return {'is_error': True, 'error_log': "Please select the group by field"}
        if not self.display_field_ids:
            return {'is_error': True, 'error_log': "Please select the field to display data"}

        if self.type == 'area':
            actual_type = 'line'
        elif self.type == 'h_bar':
            actual_type = 'bar'
        else:
            actual_type = self.type

        all_fields_data = {}
        group_fields = []
        group_fields_data = {}
        fields_list = []
        fields_agg = []
        fields_data = {}
        data_domains = []
        show_records = True

        if self.group_field_id:
            group_field = self.group_field_id.name
            all_fields_data[self.group_field_id.id] = group_field
            if self.group_field_type in ['date', 'datetime']:
                if not self.group_date_aggregates:
                    return {'is_error': True, 'error_log': "Please select the Group by date aggregation"}
                group_field += ':' + self.group_date_aggregates
            group_fields.append(group_field)
            group_fields_data[group_field] = {
                'label': self.group_field_id.field_description,
                'ttype': self.group_field_type,
                'field_id': self.group_field_id
            }

        if self.sub_group_field_id:
            sub_group_field = self.sub_group_field_id.name
            all_fields_data[self.sub_group_field_id.id] = sub_group_field
            if self.sub_group_field_type in ['date', 'datetime']:
                if not self.sub_group_date_aggregates:
                    return {'is_error': True, 'error_log': "Please select the Sub-group by date aggregation"}
                sub_group_field += ':' + self.sub_group_date_aggregates
            group_fields.append(sub_group_field)
            group_fields_data[sub_group_field] = {
                'label': self.sub_group_field_id.field_description,
                'ttype': self.sub_group_field_type,
                'field_id': self.sub_group_field_id
            }

        for field in self.display_field_ids.sorted('sequence'):
            if not field.field_aggregation_id:
                return {'is_error': True, 'error_log': "Please select the aggregation for the field: " + field.name}
            field_name = f"{field.field_id.name}_{field.field_aggregation_id.aggregate_value}" if field.field_aggregation_id else field.field_id.name
            field_agg = f"{field_name}:{field.field_aggregation_id.aggregate_value}({field.field_id.name})"

            fields_agg.append(field_agg)
            fields_list.append(field_name)
            all_fields_data[field.field_id.id] = field_name
            fields_data[field_name] = {
                'label': field.name,
                'ttype': field.field_id.ttype
            }

        limit = self.records_limit if self.records_limit else None
        orderby = self.process_sort_order(all_fields_data)

        group_result = self.env[self.model_id.model].read_group(domain, fields_agg, group_fields, offset=0, limit=limit,
                                                                orderby=orderby, lazy=False)
        formatted_result = []
        for result in group_result:
            temp_dict = {}
            for key, value in group_fields_data.items():
                if value['ttype'] in ['many2one', 'many2many']:
                    temp_dict[key] = result[key][1] if result[key] else False
                elif value['ttype'] == 'selection':
                    temp_dict[key] = value['field_id'].selection_ids.filtered(lambda l: l.value == result[key]).name
                else:
                    temp_dict[key] = result[key]
            for key, value in fields_data.items():
                temp_dict[key] = result[key]
            if show_records:
                temp_dict['__domain'] = result['__domain']
            formatted_result.append(temp_dict)

        if chart_type == 'field_grouped' or chart_type == 'simple' or (chart_type == 'field_stacked' and not self.sub_group_field_id):
            series = []
            if chart_type == 'field_stacked':
                for i in fields_list:
                    series.append({
                        "type": actual_type,
                        "name": fields_data[i]["label"],
                        "stack": group_fields[0],
                        "label": {
                            "show": self.display_data_value,
                            "position": "outside"
                        }
                    })
            else:
                for i in fields_list:
                    series.append({
                        "type": actual_type,
                        "name": fields_data[i]["label"],
                        "label": {
                            "show": self.display_data_value,
                            "position": "outside"
                        }
                    })
            options = {
                "dataset": {
                    "dimensions": group_fields + fields_list,
                    "source": formatted_result
                },
                "xAxis": [{
                    "type": 'category',
                    "axisLabel": {
                        "show": True,
                        "rotate": 50 if self.type != 'h_bar' else 0,
                        "width": 300,
                        "overflow": "truncate"
                    }
                }],
                "yAxis": {},
                "series": series
            }
            if show_records:
                data_domains = [data['__domain'] for data in formatted_result]

            return {'options': options, 'data_domains': data_domains, 'chart_basic_info': self.get_bar_line_specific_options()}

        elif chart_type == 'field_stacked' or chart_type == 'group_stacked' or chart_type == 'grouped_grouped' or chart_type == 'stacked_stacked' or chart_type == 'group_grouped':
            group_values = []
            sub_group_values = []

            for entry in formatted_result:
                if entry[group_fields[0]] not in group_values:
                    group_values.append(entry[group_fields[0]])
                if entry[group_fields[1]] not in sub_group_values:
                    sub_group_values.append(entry[group_fields[1]])

            series_data = []
            for sub_value in sub_group_values:
                temp_domain = []
                for field in fields_list:
                    temp_list = []
                    for value in group_values:
                        data = [d[field] for d in formatted_result if
                                d[group_fields[0]] == value and d[group_fields[1]] == sub_value]
                        if data:
                            temp_list.append(data[0])
                        else:
                            temp_list.append(0)
                    temp_data = {
                        'name': sub_value + ", " + fields_data[field]['label'],
                        'type': actual_type,
                        'data': temp_list,
                        "label": {
                            "show": self.display_data_value,
                            "position": "inside"
                        }
                    }
                    if chart_type == 'field_stacked':
                        temp_data['stack'] = sub_value
                    elif chart_type == 'group_stacked':
                        temp_data['stack'] = field
                    elif chart_type == 'stacked_stacked':
                        temp_data['stack'] = True
                    series_data.append(temp_data)
                if show_records:
                    for value in group_values:
                        temp_domain.append([d['__domain'] for d in formatted_result if
                                            d[group_fields[0]] == value and d[group_fields[1]] == sub_value])
                    data_domains.append(temp_domain)

            options = {"xAxis": [{
                    "type": 'category',
                    "data": group_values,
                    "axisLabel": {
                        "show": True,
                        "rotate": 50,
                        "width": 300,
                        "overflow": "truncate"
                    }
                }],
                "yAxis": [
                    {
                        "type": 'value'
                    }
                ],
                "series": series_data
            }

            return {'options': options, 'chart_basic_info': self.get_bar_line_specific_options(), 'fields_count': len(fields_list),
                    'data_domains': data_domains, 'sub_available': bool(self.sub_group_field_id)}

        return {'is_error': True, 'error_log': "Something went wrong. Please check the chart configurations"}

    @api.readonly
    def _get_pie_sql_data(self, sql_query):
        if not sql_query:
            return {'is_error': True, 'error_log': "Please enter the query"}

        try:
            self.env.cr.execute(sql_query)
            results = self.env.cr.dictfetchall()
        except Exception as e:
            return {'is_error': True, 'error_log': str(e)}

        if not results:
            return {'is_error': True, 'error_log': "Query returned no results"}

        all_fields = list(results[0].keys())
        group_field, fields_data = all_fields[0], all_fields[1:]

        series_data = []
        each_radius = {'pie': 80, 'h_pie': 130, 'doughnut': 40, 'h_doughnut': 80}.get(self.type, 90) / len(fields_data)

        for index, field in enumerate(fields_data):
            series_data.append({
                "name": field,
                "data": [{'value': result[field], 'name': result[group_field]} for result in results],
                "startAngle": 180 if self.type in ['h_doughnut', 'h_pie'] else 0,
                "endAngle": 360,
                "type": 'pie',
                "radius": [f"{40 + (each_radius * index) + 1}%", f"{40 + each_radius * (index + 1)}%"]
                if self.type not in ['pie', 'h_pie']
                else [f"{(each_radius * index) + 1}%", f"{each_radius * (index + 1)}%"],
                "minShowLabelAngle": 0 if self.display_data_value else 360,
            })

        if self.type in ['h_doughnut', 'h_pie']:
            for data in series_data:
                data['center'] = ['50%', '70%']

        return {
            "options": {"series": series_data},
            "chart_basic_info": self.get_pie_specific_options(),
            "data_domains": [],
            "display_label": self.display_data_value,
            "label_format": self.pie_label_format,
        }

    def _get_pie_data(self, domain):
        if not self.model_id:
            return {'is_error': True, 'error_log': "Please select the model name"}
        if not self.group_field_id:
            return {'is_error': True, 'error_log': "Please select the group by"}
        if not self.display_field_ids:
            return {'is_error': True, 'error_log': "Please select the fields to display data"}

        group_fields, fields_agg, series_data, data_domains = [], [], [], []
        group_fields_data, fields_data, all_fields_data = {}, {}, {}
        show_records = True

        group_field = self.group_field_id.name
        all_fields_data[self.group_field_id.id] = group_field

        if self.group_field_type in {'date', 'datetime'}:
            if not self.group_date_aggregates:
                return {'is_error': True, 'error_log': "Please select the date aggregate"}
            group_field += f":{self.group_date_aggregates}"

        group_fields.append(group_field)
        group_fields_data[group_field] = {
            'label': self.group_field_id.field_description,
            'ttype': self.group_field_type
        }

        for field in self.display_field_ids.sorted('sequence'):
            if not field.field_aggregation_id:
                return {'is_error': True, 'error_log': f"Please select the aggregation for the field: {field.name}"}

            field_name = f"{field.field_id.name}_{field.field_aggregation_id.aggregate_value}"
            field_agg = f"{field_name}:{field.field_aggregation_id.aggregate_value}({field.field_id.name})"

            fields_agg.append(field_agg)
            fields_data[field_name] = field.name
            all_fields_data[field.field_id.id] = field_name

        group_result = self.env[self.model_id.model].read_group(
            domain, fields_agg, group_fields,
            limit=self.records_limit if self.records_limit >0 else None,
            orderby=self.process_sort_order(all_fields_data)
        )

        radius_map = {
            'pie': 80, 'h_pie': 130,
            'doughnut': 40, 'h_doughnut': 80
        }
        each_radius = radius_map.get(self.type, 90) / max(len(fields_agg), 1)

        for index, field in enumerate(fields_data):
            values, temp_domains = [], []
            for result in group_result:
                if self.group_field_type in ['many2one', 'many2many']:
                    group_value = result[group_field][1] if result[group_field] else False
                elif self.group_field_type == 'selection':
                    group_value = self.group_field_id.selection_ids.filtered(lambda l: l.value == result[group_field]).name
                else:
                    group_value = result[group_field]
                temp_dict = {'value': result[field], 'name': group_value}
                if show_records:
                    temp_domains.append(result['__domain'])
                values.append(temp_dict)

            data_domains.append(temp_domains)
            series_data.append({
                "name": fields_data[field],
                "data": values,
                "startAngle": 180 if self.type in {'h_doughnut', 'h_pie'} else 0,
                "endAngle": 360,
                "type": 'pie',
                "radius": [
                    f"{(each_radius * index) + 1}%",
                    f"{each_radius * (index + 1)}%"
                ] if self.type in {'pie', 'h_pie'} else [
                    f"{40 + (each_radius * index) + 1}%",
                    f"{40 + each_radius * (index + 1)}%"
                ],
                "minShowLabelAngle": 0 if self.display_data_value else 360,
            })

        # Adjust center for half-doughnut and half-pie charts
        if self.type in {'h_doughnut', 'h_pie'}:
            for data in series_data:
                data['center'] = ['50%', '70%']

        return {
            'options': {"series": series_data},
            'chart_basic_info':  self.get_pie_specific_options(),
            'data_domains': data_domains,
            'display_label': self.display_data_value,
            'label_format': self.pie_label_format
        }

    def _get_scatter_sql_data(self, sql_query):

        if not sql_query:
            return {'is_error': True, 'error_log': "Please enter the query"}

        try:
            self.env.cr.execute(sql_query)
            results = self.env.cr.dictfetchall()
        except Exception as e:
            return {'is_error': True, 'error_log': str(e)}

        if not results:
            return {'is_error': True, 'error_log': "Query returned no results"}

        all_fields = list(results[0].keys())
        group_field_name, field_name = all_fields[0], all_fields[1]
        scatter_data = []
        for data in results:
            scatter_data.append([data[group_field_name], data[field_name]])

        return {
            'options': {
                "series": [{
                    'symbolSize': 10,
                    'data': scatter_data,
                    'type': 'scatter'
                }],
                'xAxis': {},
                'yAxis': {},
            },
            'data_domains': [],
            'chart_basic_info': self.get_scatter_specific_options()
        }

    def _get_scatter_data(self, domain):
        if not self.model_id:
            return {'is_error': True, 'error_log': "Please select the model name"}
        if not self.scatter_x:
            return {'is_error': True, 'error_log': "Please select the scatter X"}
        if not self.scatter_y:
            return {'is_error': True, 'error_log': "Please select the scatter Y"}
        if not self.scatter_y_agg:
            return {'is_error': True, 'error_log': "Please select the scatter Y aggregation"}

        group_field_name = self.scatter_x.name
        field_name = self.scatter_y.name
        field_data = field_name + ':' + self.scatter_y_agg.aggregate_value
        all_fields_data = {
            self.scatter_x.id: group_field_name,
            self.scatter_y.id: field_name,
        }

        group_result = self.env[self.model_id.model].read_group(
            domain, [field_data], [group_field_name],
            limit=self.records_limit if self.records_limit >0 else None,
            orderby=self.process_sort_order(all_fields_data)
        )

        scatter_data = []
        data_domains = []
        for data in group_result:
            scatter_data.append([data[group_field_name], data[field_name]])
            data_domains.append(data['__domain'])

        return {
            'options': {
                "series": [{
                    'symbolSize': 10,
                    'data': scatter_data,
                    'type': 'scatter'
                }],
                'xAxis': {},
                'yAxis': {},
            },
            'data_domains': data_domains,
            'chart_basic_info': self.get_scatter_specific_options()
        }

    def _get_funnel_sql_data(self, sql_query):
        if not sql_query:
            return {'is_error': True, 'error_log': "Please enter the query"}

        try:
            self.env.cr.execute(sql_query)
            results = self.env.cr.dictfetchall()
        except Exception as e:
            return {'is_error': True, 'error_log': str(e)}

        if not results:
            return {'is_error': True, 'error_log': "Query returned no results"}

        all_fields = list(results[0].keys())
        group_field_name, field_name = all_fields[0], all_fields[1]
        funnel_data = []
        for data in results:
            funnel_data.append({
                'name': data[group_field_name],
                'value': data[field_name],
            })

        return {
            'options': {
                "series": [{
                    'data': funnel_data,
                    'type': 'funnel'
                }],
            },
            'data_domains': [],
            'chart_basic_info': self.get_scatter_specific_options()
        }

    def _get_funnel_data(self, domain):
        if not self.model_id:
            return {'is_error': True, 'error_log': "Please select the model name"}
        if not self.group_field_id:
            return {'is_error': True, 'error_log': "Please select the group by field"}
        if not self.display_field_id:
            return {'is_error': True, 'error_log': "Please select the Field to display data"}
        if not self.display_field_agg:
            return {'is_error': True, 'error_log': "Please select the Aggregation"}

        group_field_name = self.group_field_id.name
        field_name = self.display_field_id.name
        field_data = field_name + ':' + self.display_field_agg.aggregate_value
        all_fields_data = {
            self.group_field_id.id: group_field_name,
            self.display_field_id.id: field_name,
        }

        group_result = self.env[self.model_id.model].read_group(
            domain, [field_data], [group_field_name],
            limit=self.records_limit if self.records_limit > 0 else None,
            orderby=self.process_sort_order(all_fields_data)
        )

        funnel_data = []
        data_domains = []
        for data in group_result:
            if self.group_field_type in ['many2one', 'many2many']:
                group_value = data[group_field_name][1] if data[group_field_name] else False
            elif self.group_field_type == 'selection':
                group_value = self.group_field_id.selection_ids.filtered(lambda l: l.value == data[group_field_name]).name
            else:
                group_value = data[group_field_name]
            funnel_data.append({
                'name': group_value,
                'value': data[field_name],
            })
            data_domains.append(data['__domain'])

        return {
            'options': {
                "series": [{
                    'data': funnel_data,
                    'type': 'funnel'
                }],
            },
            'data_domains': data_domains,
            'chart_basic_info': self.get_scatter_specific_options()
        }


    def process_sql_query(self, date_filter, domain):
        sql_query = self.input_query
        if not sql_query:
            return ''

        if 'dm#uid' in sql_query:
            sql_query = sql_query.replace('dm#uid', self._uid)
        if 'dm#allowed_company_ids' in sql_query:
            sql_query = sql_query.replace('dm#allowed_company_ids', str(self.env.context.get('allowed_company_ids', [])))
        if 'dm#user_lang' in sql_query:
            sql_query = sql_query.replace('dm#user_lang', str(self.env.context.get('lang', [])))

        datetime_data = set()
        date_data = set()
        models_data = set()

        query_words = sql_query.split()
        for word in query_words:
            if 'filter_datetime#' in word:
                datetime_data.add(word)
            elif 'filter_date#' in word:
                date_data.add(word)
            elif 'filter_model#' in word:
                models_data.add(word)

        for model_word in models_data:
            query_domain = ''
            operator, current_model_name, alias_name = model_word.split('#')[1:]
            model_id = self.sudo().env[current_model_name]
            domain_data = self.get_default_domain(current_model_name) + self.process_filter_domain(domain, current_model_name)
            if domain_data:
                test_query = expression.expression(domain_data, model_id, alias_name).query
                test_query = list(test_query._where_clauses[0])
                query_domain = test_query[0]
                parameters = test_query[1]
                for para in parameters:
                    if isinstance(para, tuple):
                        if len(para) == 1:
                            para = str(para)[:-2]+')'
                    elif isinstance(para, str):
                        para = "'" + para + "'"
                    query_domain = query_domain.replace("%s", str(para), 1)
                query_domain = operator + ' ' + query_domain
            sql_query = sql_query.replace(model_word, query_domain)

        for datetime_word in datetime_data:
            query_domain = ''
            operator, current_model_name, alias_name, field_name = datetime_word.split('#')[1:]
            model_id = self.sudo().env[current_model_name]
            datetime_domain = self.get_datetime_domain(date_filter, field_name, 'datetime')
            if datetime_domain:
                test_query = expression.expression(datetime_domain, model_id, alias_name).query
                test_query = list(test_query._where_clauses[0])
                query_domain = test_query[0]
                parameters = test_query[1]
                for para in parameters:
                    query_domain = query_domain.replace("%s", "'"+para+"'", 1)
                query_domain = operator + ' ' + query_domain
            sql_query = sql_query.replace(datetime_word, query_domain)

        for date_word in date_data:
            query_domain = ''
            operator, current_model_name, alias_name, field_name = date_word.split('#')[1:]
            model_id = self.sudo().env[current_model_name]
            datetime_domain = self.get_datetime_domain(date_filter, field_name, 'date')
            if datetime_domain:
                test_query = expression.expression(datetime_domain, model_id, alias_name).query
                test_query = list(test_query._where_clauses[0])
                query_domain = test_query[0]
                parameters = test_query[1]
                for para in parameters:
                    query_domain = query_domain.replace("%s", "'"+para+"'", 1)
                query_domain = operator + ' ' + query_domain
            sql_query = sql_query.replace(datetime_word, query_domain)

        return sql_query

    def get_charts_data(self, dashboard_filters=(), datetime_filter={}):
        datetime_data = {"datetime_start": False, "datetime_end": False, "date_start": False, "date_end": False}
        if datetime_filter and datetime_filter.get('type', False) != 'all':
            if datetime_filter['type'] == 'record':
                filter_rec = self.env['date.filters'].browse(datetime_filter['id'])
                datetime_data.update({
                    "datetime_start": filter_rec.datetime_start,
                    "datetime_end": filter_rec.datetime_end,
                    "date_start": filter_rec.date_start,
                    "date_end": filter_rec.date_end,
                })
            elif datetime_filter['type'] == 'custom':
                datetime_data.update({
                    "datetime_start": datetime_filter.get("datetime_start"),
                    "datetime_end": datetime_filter.get("datetime_end"),
                    "date_start": datetime_filter.get("date_start"),
                    "date_end": datetime_filter.get("date_end"),
                })

        all_charts_data = {}
        for chart in self:
            if not chart.dashboard_id.has_dashboard_access:
                raise AccessError(_("Access Denied"))
            chart = chart.sudo()
            if chart.use_sql:
                sql_query = chart.process_sql_query(datetime_data, dashboard_filters) if chart.type != 'list' else ''
                result_data = {}
                number_system_data = chart.chart_number_system_format()
                chart_data = {
                    'type': chart.type,
                    'id': chart.id,
                    'title': chart.name,
                    'number_system_data': number_system_data,
                    'is_sql': True,
                    'show_records': False
                }
                if chart.type == 'card':
                    result_data = chart._get_card_sql_data(sql_query)
                elif chart.type in ['bar', 'line', 'h_bar', 'area']:
                    result_data = chart._get_bar_line_sql_data(sql_query)
                elif chart.type in ['pie', 'h_pie', 'doughnut', 'h_doughnut']:
                    result_data = chart._get_pie_sql_data(sql_query)
                elif chart.type == 'list':
                    result_data = chart.get_list_sql_data([datetime_data, dashboard_filters])
                elif chart.type == 'scatter':
                    result_data = chart._get_scatter_sql_data(sql_query)

                chart_data.update(result_data)
                all_charts_data[chart.id] = chart_data
            else:
                domain_apply = chart.get_default_domain(chart.model_name) + chart.process_filter_domain(dashboard_filters, chart.model_name)
                datetime_domain = chart.get_datetime_domain(datetime_data, chart.datetime_filter_field.name, chart.datetime_filter_field.ttype)
                domain_apply += datetime_domain
                number_system_data = chart.chart_number_system_format()
                chart_data = {
                    'model': chart.model_name,
                    'list_view': chart.sudo().list_view_id.xml_id if chart.sudo().sudo().list_view_id else
                    self.env[
                        'ir.ui.view'].sudo().search([('model', '=', chart.model_name), ('type', '=', 'list')],
                                                    limit=1).xml_id,
                    'form_view': chart.sudo().form_view_id.xml_id if chart.sudo().form_view_id else
                    self.env[
                        'ir.ui.view'].sudo().search([('model', '=', chart.model_name), ('type', '=', 'form')],
                                                    limit=1).xml_id,
                    'type': chart.type,
                    'id': chart.id,
                    'title': chart.name,
                    'number_system_data': number_system_data,
                    'is_sql': False,
                    'show_records': chart.show_records
                }

                result_data = {}
                if chart.type == 'card':
                    result_data = chart._get_card_data(domain_apply)
                elif chart.type in ['bar', 'line', 'h_bar', 'area']:
                    if chart.group_field_id and len(chart.display_field_ids)==1 and not chart.sub_group_field_id:
                        chart_data['bar_type'] = 'simple'
                    if chart.group_field_id and len(chart.display_field_ids)>1 and chart.sub_group_field_id and not chart.fields_stacked  and not chart.groups_stacked:
                        chart_data['bar_type'] = 'grouped_grouped'
                    elif chart.group_field_id and len(chart.display_field_ids)>1 and chart.sub_group_field_id and chart.fields_stacked and chart.groups_stacked:
                        chart_data['bar_type'] = 'stacked_stacked'
                    elif chart.group_field_id and len(chart.display_field_ids.ids)>=1 and chart.sub_group_field_id and chart.groups_stacked and not chart.fields_stacked:
                        chart_data['bar_type'] = 'group_stacked'
                    elif chart.group_field_id and len(chart.display_field_ids.ids)==1 and chart.sub_group_field_id:
                        chart_data['bar_type'] = 'group_grouped'
                    elif chart.group_field_id and len(chart.display_field_ids)>1 and chart.fields_stacked:
                        chart_data['bar_type'] = 'field_stacked'
                    elif chart.group_field_id and len(chart.display_field_ids.ids)>1 and not chart.sub_group_field_id:
                        chart_data['bar_type'] = 'field_grouped'
                    else:
                        chart_data['bar_type'] = 'simple'

                    result_data = chart._get_bar_line_data(chart_data['bar_type'], domain_apply)
                    if not result_data.get('is_error', False):
                        if chart.type == 'area':
                            for data in result_data['options']['series']:
                                data['areaStyle'] = {}
                            for data in result_data['options']['xAxis']:
                                data['boundaryGap'] = False
                        if chart.type == 'line' and chart.smooth_line:
                            for data in result_data['options']['series']:
                                data['smooth'] = True
                        if chart.type == 'line' and chart.step_line:
                            for data in result_data['options']['series']:
                                data['step'] = chart.step_position

                elif chart.type in ['pie', 'h_pie', 'doughnut', 'h_doughnut']:
                    result_data = chart._get_pie_data(domain_apply)
                elif chart.type == 'list':
                    result_data = chart.list_item_data(domain_apply)
                elif chart.type == 'scatter':
                    result_data = chart._get_scatter_data(domain_apply)
                elif chart.type == 'funnel':
                    result_data = chart._get_funnel_data(domain_apply)
                chart_data.update(result_data)
                all_charts_data[chart.id] = chart_data
        return all_charts_data


class DisplayField(models.Model):
    _name = 'field.display'
    _description = 'Dashboard Maker Chart Fields'

    name = fields.Char(string="Display name", translate=True)
    chart_id = fields.Many2one('dashboard.chart')
    model_id = fields.Many2one(related='chart_id.model_id')
    list_grouped = fields.Boolean(related='chart_id.list_grouped')
    field_id = fields.Many2one('ir.model.fields', domain="[('model_id','=',model_id), ('store','=',True), ('ttype', 'not in', ['one2many', 'one2many'])]", string="Field")
    field_type = fields.Selection(related='field_id.ttype')
    field_aggregation_id = fields.Many2one('fields.aggregates', domain="[('field_type','=',field_type)]", string="Aggregation")
    sequence = fields.Integer()

    @api.onchange('field_id')
    def update_name(self):
        for rec in self:
            rec.name = rec.field_id.field_description

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            if rec.field_id:
                name_translations = rec.field_id.get_field_translations('field_description')[0]
                if name_translations:
                    for translation in name_translations:
                        rec._update_field_translations('name', {translation['lang']: translation['value']})
        return records


class FilterMapping(models.Model):
    _name = 'filter.mapping'
    _description = 'Dashboard Maker Filters Mapping'

    chart_id = fields.Many2one('dashboard.chart')
    dashboard_filters_ids = fields.Many2many(related='chart_id.dashboard_id.filter_model_ids')
    filter_id = fields.Many2one('ir.model', domain="[('id', 'in', dashboard_filters_ids), ('id', '!=', chart_model_id), ('transient','=',False)]", string="Filter model")
    model_name = fields.Char(related='filter_id.model')
    field_ids = fields.Many2many('ir.model.fields', domain="[('model_id','=',chart_model_id), ('relation','=',model_name), ('store','=',True)]", string="Mapping Field")
    chart_model_id = fields.Many2one('ir.model', string="Curren Chart Model", domain="[('transient','=',False)]")

    @api.onchange('filter_id')
    def _onchange_filter_id(self):
        for rec in self:
            self.field_ids = False


class SelectFields(models.Model):
    _name = 'fields.selection'
    _description = 'Dashboard Maker Group Fields Selection'

    chart_id = fields.Many2one('dashboard.chart')
    model_id = fields.Many2one(related='chart_id.model_id')
    sequence = fields.Integer()
    field_id = fields.Many2one('ir.model.fields', domain="[('model_id','=',model_id), ('store','=',True), ('ttype', 'not in', ['binary', 'one2many'])]", string="Field")
    field_type = fields.Selection(related='field_id.ttype')
    date_aggregates = fields.Selection([('day', 'Day'), ('week', 'Week'), ('month', 'Month'), ('quarter', 'Quarter'), ('year', 'Year')])
    display_string = fields.Char(string="Display name", translate=True)

    @api.onchange('field_id')
    def update_display_string(self):
        for rec in self:
            rec.display_string = rec.field_id.field_description

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            if rec.field_id:
                name_translations = rec.field_id.get_field_translations('field_description')[0]
                if name_translations:
                    for translation in name_translations:
                        rec._update_field_translations('display_string', {translation['lang']: translation['value']})
        return records


class SortField(models.Model):
    _name ='sort.field'
    _description = 'Dashboard Maker Sort Fields'

    chart_id = fields.Many2one('dashboard.chart')
    model_id = fields.Many2one(related='chart_id.model_id')
    field_id = fields.Many2one('ir.model.fields', string="Name", domain="[('model_id', '=', model_id), ('store','=',True), ('ttype', 'not in', ['binary', 'one2many'])]")
    sort_type = fields.Selection([('ASC ', 'Ascending'), ('DESC', 'Descending')], string="Sort type")
    sequence = fields.Integer()


class GroupsDataFilter(models.Model):
    _name = 'groups.data.filter'
    _description = 'Dashboard Maker Chart Data Filter'

    chart_id = fields.Many2one('dashboard.chart')
    model_id = fields.Many2one('ir.model', string='Model name', domain="[('transient','=',False)]")
    model_name = fields.Char(related='model_id.model')
    domain = fields.Text(string="Domain")
    group_ids = fields.Many2many('res.groups', string="Apply For Groups")
    sequence = fields.Integer(string="Sequence")
