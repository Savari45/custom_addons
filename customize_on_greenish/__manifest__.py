# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'MRP in Invoices',
    'version': '18.0.1.0.1',
    'description': 'Adds Expiry Dates and Lots and Serial into Invoice/Bill Move Lines from its related stock moves',
    'sequence': 1,
    'author': 'Alan Technologies',
    'company': 'Alan Technologies',
    'maintainer': 'Alan Technologies',
    'website': "https://alantechnologies.in/",
    'category': 'Invoice',
    'summary': 'Add the MRP in the Product and Incoice Lines ',
    'depends': ['base', 'stock', 'sale', 'account', 'purchase'],
    'data': [
        # 'security/ir.model.access.csv',
        'models/fields.xml',
        'views/inherit_invoice.xml',
        'views/inherit_product_template.xml',
        'views/sale_order_line.xml',
        'report/inherit_invoice_report.xml',
        'actions/dynamic_cash_rounding.xml',
        'report/custom_header.xml',

        # 'report/paper_format.xml',
    ],
    'images': ['static/description/banner.gif'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
