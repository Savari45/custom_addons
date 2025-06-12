# -*- coding: utf-8 -*-

from . import models
from . import wizard

def uninstall_hook(env):
    created_dashboards = env['dashboard.dashboard'].search([])
    created_dashboards.mapped('menu_id').unlink()
    created_dashboards.mapped('action_id').unlink()
