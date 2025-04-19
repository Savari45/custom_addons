# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Name Search',
    'version': '1.1',
    'author': 'Alan Technologies',
    'category': 'Sales',
    'maintainer': 'Alan Technologies',
    'summary': """Search the Customer in the mobile number """,
    'description': """

        You see the customer name in the search of the mobile number 

    """,
    'website': 'https://www.Alan technology.com/',
    'license': 'LGPL-3',
    'support': 'info@alantech.com',
    'depends': ['sale_stock', 'product','sale'],
    'data': [
        #'views/product_view.xml',
        #'views/sale_order_line.xml',
        # 'data/report_action.xml',
        # 'report/custom_report.xml',
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
    'images': ['static/description/main_screen.png'],

}
