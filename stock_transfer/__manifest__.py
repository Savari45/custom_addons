{
    'name': "Stock  Transfer",
    'description': """
        
        🔧 Technical:
        - User-friendly wizard to generate XML
        - Secure attachment management inside Odoo
        - Works seamlessly with Odoo's Accounting and Sales modules

        Developed and maintained by Alan Technologies.

    """,
    'summary': """ Generate XML file from Invoices/Sales and send it to Tax Office. | Export Sales Invoices to XML format | Send XML files to Tax Authority | Odoo 18 XML Generator.""",
    'sequence': 1,
    'author': 'Alan Technologies',
    'company': 'Alan Technologies',
    'maintainer': 'Alan Technologies',
    'website': "https://alantechnologies.in/",
    "license": "AGPL-3",
    'category': 'Accounting',
    'version': '18.0.1.0.0',
    'depends': ['base', 'sale', 'account', 'stock'],
    'data': [
         'views/inherit_stock_picking_views.xml',

    ],
    'images': ['static/description/banner.gif'],
    'installable': True,
    'auto_install': False,
    'application': True,

}
