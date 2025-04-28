{
    'name': "XML File",
    'description': """
        This module allows users to generate Excel sheets for Sale Quotations and send them as email attachments directly from the Odoo interface.

        Key Features:
        - Generate Excel (.xlsx) version of a sale quotation
        - Include product lines, customer details, totals, and more
        - Send email with Excel attachment using a email template
        - Log email activity in chatter for reference
        - User access control for sending Excel quotations

    """,
    'summary': """ Automatically generate and send Sale Quotations as Excel attachments via email.""",
    'sequence': 1,
    'author': 'Alan Technologies',
    'company': 'Alan Technologies',
    'maintainer': 'Alan Technologies',
    'website': "https://alantechnologies.in/",
    "license": "AGPL-3",
    'category': 'account',
    'version': '18.0.1.0.0',
    'depends': ['base', 'sale','account'],
    'data': [
            'wizard/xml_file.xml',
            'views/account_view.xml',
        'security/ir.model.access.csv',
    ],
    # 'images': ['static/description/banner.gif'],
    'installable': True,
    'auto_install': False,
    'application': True,

}
