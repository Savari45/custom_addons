# -*- coding: utf-8 -*-

{
    'name': "POS Invoice on Receipt",
    'summary': """
        Allows to print invoice number and customer name on POS receipt.
    """,
    'description': """
        Allows to print invoice number and customer name on POS receipt.
    """,
    'author': "RDFlex",
    'company': 'RDFlex',
    'maintainer': 'RDFlex',
    'website': "https://rdflex.com",
    'category': 'Point of sale',
    'version': '1.0',
    'license': 'OPL-1',
    'depends': ['point_of_sale'],
    'images': ['static/description/banner.jpg'],
    'qweb': ['static/src/xml/pos_ticket_invoice.xml'],
        'data': [
        'views/pos_assets.xml',
    ],
}
