{
    'name': "Display the Exisitng Products list",
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
    'category': 'purchase',
    'author': 'Alan Technologies',
    'maintainer': 'Alan Technologies',
    'company': 'Alan Technologies',
    'website': "https://alantechnologies.in/",
    'license': "AGPL-3",
    'depends': ['stock'],
    'data': [
        'views/product_views.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'exisitng_product/static/src/xml/control_buttons_inherit.xml',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'sequence': 1,
}
