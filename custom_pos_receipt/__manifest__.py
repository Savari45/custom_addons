{
    'name': "Pos Receipt Custom",
    'summary': "Display only in-stock products in sale order lines and show available on-hand quantity.",
    'description': """
        
    """,
    'version': '18.0.1.0.0',
    'category': 'Sales',
    'author': 'Alan Technologies',
    'maintainer': 'Alan Technologies',
    'company': 'Alan Technologies',
    'website': "https://alantechnologies.in/",
    'license': "AGPL-3",
    'depends': ['base', 'sale', 'account', 'point_of_sale'],
    'data': [

    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'custom_pos_receipt/static/src/js/CustomOrderReceipt.js',
            'custom_pos_receipt/static/src/js/ReprintReceiptScreen.js',
            'custom_pos_receipt/static/src/xml/OrderReceipt.xml',
        ],
    },
    'images': ['static/description/banner.gif'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'sequence': 1,
}
