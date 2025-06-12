# -*- coding: utf-8 -*-
{
    'name': "Advance Employee Portal",

    'summary': "Advance Employee Portal | Employee can request from Portal | Employee can view their backend details",

    'author': "Irfan Ullah",
    'website': "https://www.youtube.com/@irfanullah",
    'category': 'Portal',
    'version': '18.0.0.1',
    # 'price': '12.00',
    # 'currency': 'USD',

    # any module necessary for this one to work correctly
    'depends': ['base', 'portal', 'hr_holidays', 'planning'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        # 'security/portal_user_group.xml',
        'views/active_warning_view.xml',
        'views/sop_violation_view.xml',
        'views/portal_announcement_view.xml',
        'views/new_menus_in_portal.xml',
        'views/employee_leave_template.xml',
        'views/sop_violation_template.xml',
        'views/active_warning_template.xml',
        'views/weekly_schedule_template.xml',
        'views/portal_announcement_template.xml',
        'views/submit_leave_request.xml',
        'views/submit_weekly_schedule_request.xml',
        'views/project_tasks.xml',
    ],
    'images': ['static/description/banner.png'],
}
