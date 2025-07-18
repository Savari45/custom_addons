{
    'name': "Internal Transfer",
    'description': """
        Easily generate XML files from Sales Invoices in Odoo and send them as attachments directly to the Tax Office.

        ✅ Key Features:
        - Export Sales Invoices to XML format
        - Include customer details, invoice lines, tax information
        - Supports SAF-T compliance for Tax Authorities (example: Angola, Portugal, etc.)
        - Send XML files directly from Odoo as attachments
        - Designed for Odoo 18, Odoo 17, and compatible versions

        📂 Use Cases:
        - Submit sales data to government tax portals
        - Generate structured invoice reports in XML
        - Simplify tax compliance and digital reporting

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

        'report/inherit_delivery_report.xml',
        'views/stock_picking_views.xml',
        'views/inherit_search_view.xml',


    ],
    'images': ['static/description/banner.gif'],
    'installable': True,
    'auto_install': False,
    'application': True,

}
