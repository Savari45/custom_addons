{
    'name': 'Purchase Order Product Wizard',
    'version': '1.0',
    'license': 'LGPL-3',
    'depends': ['purchase', 'product', 'web','base'],
    'assets': {
        'web.assets_backend': [
            'custom_purchase_order_line/static/src/js/m2o_product_wizard.esm.js',
        ],
    },

    'data': [
        'views/purchase_order_line_view.xml',
        'views/templates.xml',
        # 'wizard/product_confirmation_wizard.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
}
