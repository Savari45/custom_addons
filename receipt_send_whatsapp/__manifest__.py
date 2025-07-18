{
    'name': "Receiptsend the Whatsapp",
    'description': """
       

    """,
    'summary': """ Default set the Inter Company Transit .""",
    'sequence': 1,
    'author': 'Alan Technologies',
    'company': 'Alan Technologies',
    'maintainer': 'Alan Technologies',
    'website': "https://alantechnologies.in/",
    'support': 'alantechnologies2022@gmail.com',
    "license": "AGPL-3",
    'category': 'point of sale',
    'version': '18.0.1.0.0',
    'depends': ['point_of_sale'],
    'data': [
        'views/assets.xml',
    ],
'assets': {
        'point_of_sale.assets': [
            'pos_whatsapp/static/src/js/receipt_send.js',
            'pos_whatsapp/static/src/xml/WhatsAppButton.xml',
        ],
    },
    'images': ['static/description/banner.gif'],
    'installable': True,
    'auto_install': False,
    'application': True,

}
