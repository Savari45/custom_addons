# -*- coding: utf-8 -*-

from odoo import fields, models, api
from datetime import datetime, timedelta, timezone, time
import pytz
from dateutil.relativedelta import relativedelta


class FilterModels(models.Model):
    _name = 'filter.models'
    _description = 'Dashboard Maker Dashboard Filters'
    _rec_name = 'model_id'

    model_id = fields.Many2one('ir.model', string="Model")
    field_ids = fields.Many2many('ir.model.fields', string="Quick search fields", domain="[('model_id','=',model_id)]")
    dashboard_id = fields.Many2one('dashboard.dashboard', string='Dashboard')

    @api.onchange('model_id')
    def onchange_model_id(self):
        self.write({'field_ids': False})


class DateFilters(models.Model):
    _name = 'date.filters'
    _description = 'Dashboard Maker Date Filters'

    name = fields.Char(string="Name")
    sequence = fields.Integer(string="Sequence")
    start = fields.Integer(string="Start at")
    end = fields.Integer(string="End at")
    custom_start = fields.Date(string="Start date")
    custom_end = fields.Date(string="End date")
    period = fields.Selection([('days', 'Days'), ('weeks', 'Weeks'), ('months', 'Months'), ('years', 'Years')], string="Time period")
    datetime_start = fields.Datetime(string="Datetime start", compute="compute_start_datetime")
    datetime_end = fields.Datetime(string="Datetime end", compute="compute_end_datetime")
    date_start = fields.Date(string="Date start", compute="compute_start_datetime")
    date_end = fields.Date(string="Date end", compute="compute_end_datetime")
    dashboard_ids = fields.Many2many('dashboard.dashboard', string="Show On Dashboards")
    apply_type = fields.Selection([('start_end_at', 'Start at + End at'), ('start_end_date', 'Start Date + End Date'),
                                   ('start_end_ad', 'Start at + End Date'), ('start_end_da', 'Start Date + End at')], default='start_end_at')

    def compute_start_datetime(self):
        """Compute the start datetime based on the given period and type."""
        user_timezone = pytz.timezone(self.env.context.get('tz'))
        today = datetime.now(user_timezone).replace(hour=0, minute=0, second=0, microsecond=0)

        for rec in self:
            if rec.apply_type in {'start_end_date', 'start_end_da'}:
                start_at = user_timezone.localize(datetime.combine(rec.custom_start, time.min))
            else:
                start_at = today  # Default initialization
                match rec.period:
                    case 'days':
                        start_at += timedelta(days=rec.start)
                    case 'weeks':
                        start_of_week = today - timedelta(days=today.weekday())
                        start_at = start_of_week + timedelta(weeks=rec.start)
                    case 'months':
                        start_at = today.replace(day=1) + relativedelta(months=rec.start)
                    case 'years':
                        start_at = today.replace(year=today.year + rec.start, month=1, day=1)

            # Convert datetime to UTC and store results
            rec.datetime_start = start_at.astimezone(pytz.utc).replace(tzinfo=None)
            rec.date_start = start_at.strftime('%Y-%m-%d')

    def compute_end_datetime(self):
        """Compute the end datetime based on the given period and type."""
        user_timezone = pytz.timezone(self.env.context.get('tz'))
        today = datetime.now(user_timezone).replace(hour=0, minute=0, second=0, microsecond=0)

        for rec in self:
            if rec.apply_type in {'start_end_date', 'start_end_ad'}:
                end_at = user_timezone.localize(datetime.combine(rec.custom_end, time.max))
            else:
                end_at = today  # Default initialization
                match rec.period:
                    case 'days':
                        end_at += timedelta(days=rec.end)
                    case 'weeks':
                        start_of_week = today - timedelta(days=today.weekday())
                        end_at = start_of_week + timedelta(days=6, hours=23, minutes=59, seconds=59) + timedelta(weeks=rec.end)
                    case 'months':
                        first_day_of_this_month = today.replace(day=1)
                        end_at = (first_day_of_this_month + relativedelta(months=rec.end + 1) - timedelta(days=1))
                    case 'years':
                        end_at = today.replace(year=today.year + rec.end, month=12, day=31)

                # Set the time to the last possible moment of the given period
                end_at = end_at.replace(hour=23, minute=59, second=59, microsecond=999)

            # Convert datetime to UTC and store results
            rec.datetime_end = end_at.astimezone(pytz.utc).replace(tzinfo=None)
            rec.date_end = end_at.strftime('%Y-%m-%d')

    def prepare_date_filters(self, dashboard_id: int, default_filter: int = 0) -> list[dict]:
        """Get date filters for a given dashboard.
        Args:
            dashboard_id (int): The ID of the dashboard.
            Default_filter (int, optional): The ID of the default filter. Defaults to 0.
        Returns:
            list[dict]: A list of filter dictionaries.
        """
        filters = self.search(
            ["|", ("dashboard_ids", "in", [dashboard_id]), ("dashboard_ids", "=", False)],
            order="sequence"
        ).mapped(lambda rec: {
            "name": rec.name,
            "isActive": rec.id == default_filter,
            "id": rec.id
        })

        return [{"name": "All Time", "isActive": default_filter == 0, "id": 0}] + filters
