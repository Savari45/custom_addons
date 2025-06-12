# -*- coding: utf-8 -*-
from odoo import fields, models

class CopyDashboardWizard(models.TransientModel):
    _name = 'copy.dashboard.chart.wizard'
    _description = 'Copy dashboard item'

    dashboard_id = fields.Many2one('dashboard.dashboard', string="Destination Dashboard")
    chart_id =fields.Many2one('dashboard.chart', string="Chart")
    operation = fields.Selection([('copy', 'Copy'), ('move', 'Move')], string="Operation")

    def action_copy_chart(self):
        for rec in self:
            chart_data = rec.chart_id.copy_data()
            for data in chart_data:
                del data['grid_x']
                del data['grid_y']
                del data['grid_w']
                del data['grid_h']
                del data['grid_mobile_h']
                data['dashboard_id'] = rec.dashboard_id.id
                data['filter_mapping_ids'] = False
            self.env['dashboard.chart'].create(chart_data)

            if rec.operation == 'move':
                rec.chart_id.unlink()

                # select
                # sum(so.amount_total)
                # from sale_order as so
                # where(1 = 1) and ("so"."name"-> > 'en_US' ILIKE '%5%')
