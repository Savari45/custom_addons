{
    'name': "Generate the Pos invoice paper format is 80mm",
    'description': """
        Generate the 80 mm invoice
    """,
    'summary': """ pos_invoice.""",
    'sequence': 1,
    'author': 'Alan Technologies',
    'company': 'Alan Technologies',
    'maintainer': 'Alan Technologies',
    'website': "https://alantechnologies.in/",
    'support': 'alantechnologies2022@gmail.com',
    "license": "AGPL-3",
    'category': 'Accounting',
    'version': '18.0.1.0.0',
    'depends': ['base', 'sale', 'account','point_of_sale'],
    'data': [
       'data/report_action.xml',
        'report/custom_report.xml',
    ],
    'images': ['static/description/banner.gif'],
    'installable': True,
    'auto_install': False,
    'application': True,

}
