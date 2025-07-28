
{
    'name': "Pos Receipt Customization",
    "version": "18.0.1.0.0",
    "category": "Point of Sale",
    "summary": "Pos Receipt Customization",
    "description": """Pos Receipt Customization""",
    'author': 'Alan Technologies',
    'website': "https://alantechnologies.in/",
    'company': 'Alan Technologies',
    'maintainer': 'Alan Technologies',
    'depends': ['point_of_sale', 'sale','l10n_in_pos'],
    'data': [

    ],
    'assets': {
        'point_of_sale._assets_pos': [
         'pos_receipt/static/src/xml/custom_pos_recipt.xml',
            'pos_receipt/static/src/xml/in_pos_receipt.xml',
            'pos_receipt/static/src/js/PosOrder.js',


        ],

    },
    'images': ['static/description/banner.png'],
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
