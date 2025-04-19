# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Greenish',
    'description': 'Adds Expiry Dates and Lots and Serial into Invoice/Bill Move Lines from its related stock moves',
    'sequence': 1,
    'author': 'Alan',
    'category': 'Accounting/Accounting',
    'summary': 'Adds Expiry Dates and Lots into Invoice/Bill Move Lines from its related stock moves',
    'version': '1.0',
    'depends': ['base', 'stock', 'sale', 'account', 'purchase'],
    'data': [
        'report/custom_header.xml',
        'report/remove_header.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
