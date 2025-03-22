# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Expiry Dates in Invoice Line',
    'description': 'Adds Expiry Dates and Lots and Serial into Invoice/Bill Move Lines from its related stock moves',
    'sequence': 1,
    'author' : 'Mohamed Yaseen Dahab',
    'category': 'Accounting/Accounting',
    'summary': 'Adds Expiry Dates and Lots into Invoice/Bill Move Lines from its related stock moves',
    'version': '1.0',
    'depends': ['base','stock', 'sale','account','purchase'],
    'data': [
        'security/ir.model.access.csv',
        'views/inherit_invoice.xml',
        'report/inherit_invoice_report.xml',
    ],
    'images': ['images/main_screenshot.png'],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
