{
    'name': "Customer Phone Number Required",
    'description': """
      Create the New Customer the Phone field is must Required

    """,
    'summary': """ Customer Phone number create during the new Customer Creation""",
    'sequence': 1,
    'author': 'Alan Technologies',
    'company': 'Alan Technologies',
    'maintainer': 'Alan Technologies',
    'website': "https://alantechnologies.in/",
    "license": "AGPL-3",
    'category': 'Accounting',
    'version': '18.0.1.0.0',
    'depends': ['base'],
    'data': [

        'views/res_partner_views.xml',

    ],
    'images': ['static/description/banner.gif'],
    'installable': True,
    'auto_install': False,
    'application': True,

}
