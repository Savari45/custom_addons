# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Invoicing',
    'version': '1.3',
    'summary': 'Invoices, Payments, Follow-ups & Bank Synchronization',
    'sequence': 10,
    'description': """
Invoicing & Payments
====================
The specific and easy-to-use Invoicing system in Odoo allows you to keep track of your accounting, even when you are not an accountant. It provides an easy way to follow up on your vendors and customers.

You could use this simplified accounting in case you work with an (external) account to keep your books, and you still want to keep track of payments. This module also offers you an easy method of registering payments, without having to encode complete abstracts of account.
    """,
    'category': 'Accounting/Accounting',
    'website': 'https://www.odoo.com/app/invoicing',
    'depends': ['base_setup', 'onboarding', 'product', 'analytic', 'portal', 'digest','sale','account','purchase','sale_management'],
    'data': [
       'views/sale_order_line.xml',
        'report/custom_report.xml',
        'data/report_action.xml',
        #'security/ir.model.access.csv',
        ],

    'installable': True,
    'application': True,
 'license': 'LGPL-3',
}