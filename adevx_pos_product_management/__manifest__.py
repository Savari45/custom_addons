{
    'name': "POS Product Management",
    'summary': """POS Product Management""",
    'description': """POS Product Management""",

    'category': 'Sales/Point of Sale',
    'author': 'Adevx',
    'license': "OPL-1",
    'website': 'https://adevx.com',
    "price": 0,
    "currency": 'USD',

    'depends': ['point_of_sale', 'sale_stock'],
    'data': [
        # views
        'views/pos_config.xml',
    ],
    "assets": {
        "point_of_sale._assets_pos": [
            "adevx_pos_product_management/static/src/**/*"
        ]
    },

    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
