# -*- coding: utf-8 -*-
from odoo import fields, models, api,  _
from odoo.exceptions import AccessError

fields_operators = {
    'many2one': 'in',
    'many2many': 'in',
    'selection': 'in',
    'char': 'ilike',
    'text': 'ilike',
    'html': 'ilike',
    'json': 'ilike',
    'date': '=',
    'integer': '=',
    'float': '=',
    'monetary': '=',
    'boolean': 'in',
}


class MainDashboard(models.Model):
    _name = 'dashboard.dashboard'
    _description = 'Dashboard Maker Dashboards'
    _order = "priority desc, name asc, id desc"

    name = fields.Char(string="Menu Name", translate=True)
    action_name = fields.Char(string="Dashboard Name", translate=True)
    chart_ids = fields.One2many('dashboard.chart', 'dashboard_id', string="Charts")
    group_ids = fields.Many2many('res.groups', string="Group Access")
    filter_model_ids = fields.Many2many('ir.model', compute="_get_filter_model_ids")
    filter_models_ids = fields.One2many('filter.models', 'dashboard_id', string="Filter Models")
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'High'),
    ], default='0', string="Priority")
    sequence = fields.Integer(string="Sequence")
    parent_menu_id = fields.Many2one('ir.ui.menu', string="Show Under Menu")
    menu_icon = fields.Binary(string="Menu Icon")
    menu_id = fields.Many2one('ir.ui.menu')
    action_id = fields.Many2one('ir.actions.client')
    is_active = fields.Boolean(string="Active", default=True)
    has_dashboard_access = fields.Boolean(compute="_check_dashboard_access")
    date_filter_default = fields.Many2one('date.filters', string="Default Date filter")

    @api.depends('group_ids')
    def _check_dashboard_access(self):
        for rec in self:
            if self.env.user.has_group('dashboard_maker.group_dashboard_maker_admin'):
                rec.has_dashboard_access = True
            else:
                if not self.is_active:
                    rec.has_dashboard_access = False
                elif rec.group_ids:
                    rec_groups = list(rec.group_ids._ensure_xml_id().values())
                    groups_string = ",".join(rec_groups)
                    if self.env.user.has_groups(groups_string):
                        rec.has_dashboard_access = True
                    else:
                        rec.has_dashboard_access = False
                else:
                    rec.has_dashboard_access = True

    def unlink(self):
        if self.sudo().menu_id:
            self.sudo().menu_id.unlink()
        if self.sudo().action_id:
            self.sudo().action_id.unlink()
        return super().unlink()

    def _get_filter_model_ids(self):
        filter_models = self.env['ir.model']
        for filter in self.filter_models_ids:
            filter_models += filter.model_id
        self.filter_model_ids = filter_models.ids

    @api.onchange('is_active')
    def change_menu_state(self):
        if self.menu_id:
            self.menu_id.active = self.is_active

    @api.onchange('name')
    def change_menu_name(self):
        if self.menu_id:
            self.menu_id.name = self.name
            name_translations = self.get_field_translations('name')[0]
            if name_translations:
                for translation in name_translations:
                    self.menu_id._update_field_translations('name', {translation['lang']: translation['value']})

    @api.onchange('action_name')
    def change_action_name(self):
        if self.action_id:
            self.action_id.name = self.action_name
            name_translations = self.get_field_translations('action_name')[0]
            if name_translations:
                for translation in name_translations:
                    self.action_id._update_field_translations('name', {translation['lang']: translation['value']})

    @api.onchange('sequence')
    def change_menu_sequence(self):
        if self.menu_id:
            self.menu_id.sequence = self.sequence

    @api.onchange('group_ids')
    def change_menu_access(self):
        if self.menu_id:
            self.menu_id.groups_id = False
            self.menu_id.groups_id = self.group_ids.ids

    @api.onchange('menu_icon')
    def change_menu_icon(self):
        if self.menu_id:
            self.menu_id.web_icon_data = self.menu_icon

    @api.onchange('parent_menu_id')
    def change_menu(self):
        if self.menu_id:
            self.menu_id.parent_id = self.parent_menu_id.id

    @api.model_create_multi
    def create(self, values):
        dashboards = super(MainDashboard, self).create(values)

        for dashboard in dashboards:
            client_action = self.env['ir.actions.client'].sudo().create([{
                'name': dashboard.action_name,
                'res_model': 'dashboard.dashboard',
                'tag': 'dashboard_maker',
                'context': {'dashboard_record_id': dashboard.id},
            }])

            menu_data = {
                'name': dashboard.name,
                'sequence': dashboard.sequence,
                'parent_id': dashboard.parent_menu_id.id,
                'web_icon_data': dashboard.menu_icon,
                'active': dashboard.is_active,
                'groups_id': dashboard.group_ids.ids,
                'action': "ir.actions.client," + str(client_action.id),
            }

            menu_id = self.env['ir.ui.menu'].sudo().create([menu_data])
            dashboard.menu_id = menu_id.id
            dashboard.action_id = client_action.id

        return dashboards

    def get_grid_data(self, is_mobile):
        return [{
            'x': rec.grid_x,
            'y': rec.grid_y,
            'w': rec.grid_w,
            'h': rec.grid_mobile_h if is_mobile else rec.grid_h,
            'id': rec.id,
            'type': rec.type,
        } for rec in self.chart_ids]

    def dashboard_basic_data(self, is_mobile=False):
        if not self.has_dashboard_access:
            raise AccessError(_("Access Denied"))
        self = self.sudo()
        date_filters = self.env['date.filters'].prepare_date_filters(self.id, self.date_filter_default.id)
        self.get_filter_models_data()
        filter_models_data = self.get_filter_models_data()
        return {'date_filters': date_filters, 'is_admin': self.env.user.has_group('dashboard_maker.group_dashboard_maker_admin'),
                'filter_models_data': filter_models_data if filter_models_data else False, 'grid_data': self.get_grid_data(is_mobile)}

    def get_filter_models_data(self):
        filter_models_data = []
        for filter_rec in self.filter_models_ids:
            fields_data = filter_rec.field_ids.mapped(lambda f: {'name': f.name, 'label':f.field_description, 'operator': fields_operators[f.ttype]})
            filter_models_data.append({
                'name': filter_rec.model_id.name,
                'model': filter_rec.model_id.model,
                'id': filter_rec.id,
                'fields_data': fields_data
            })
        return filter_models_data

    def open_dashboard_preview(self):
        url = self.env['ir.config_parameter'].sudo().get_param('web.base.url') + '/odoo/action-' + str(self.action_id.id)
        return {
            'url': url,
            'target': 'self',
            'type': 'ir.actions.act_url',
        }

    def open_dashboard_items(self):
        return {
            'name': _('Dashboard Charts'),
            'view_mode': 'list,form',
            'domain': [('dashboard_id', '=', self.id)],
            'res_model': 'dashboard.chart',
            'type': 'ir.actions.act_window',
            'context': {
                'default_dashboard_id': self.id
            }
        }
