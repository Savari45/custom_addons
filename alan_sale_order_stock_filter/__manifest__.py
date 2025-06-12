{
    'name': "Sale Order Stock Filter  | Sales Order Product Stock Availability Filter | Show Available Stock in Sale Order Lines | Odoo Sales: Hide Products with No Stock",
    'summary': "Display only in-stock products in sale order lines and show available on-hand quantity.",
    'description': """
        This module enhances the sales process by ensuring only products with positive stock are available for selection in sale order lines.

        Key Features:
        - Shows on-hand quantity of products in the sale order line.
        - Filters out products with zero or negative stock.
        - Prevents selection of unavailable products during sales order creation.
        - Improves accuracy and avoids overselling.
    """,
    'version': '18.0.1.0.0',
    'category': 'Sales',
    'author': 'Alan Technologies',
    'maintainer': 'Alan Technologies',
    'company': 'Alan Technologies',
    'website': "https://alantechnologies.in/",
    'license': "AGPL-3",
    'depends': ['base', 'sale', 'stock'],
    'data': [
        'views/sale_order_stock_filter_view.xml',
    ],
    'images': ['static/description/banner.gif'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'sequence': 1,
}
