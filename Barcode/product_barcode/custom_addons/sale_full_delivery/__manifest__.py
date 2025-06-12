# -*- coding: utf-8 -*-
{
    'name': "Sale customize",
    'summary': "This module customizes the sale process.",
    'author': "My Company",
    'website': "http://www.yourcompany.com",
    'category': 'Sales',
    'version': '17.0.1.0',
    'depends': [
        'sale','sale_stock','stock','account'


    ],
    'data': [
        'data/ir_cron_job.xml',
        'views/views.xml',

    ],

    'installable': True,
    'application': False,
    'auto_install': False,
}
