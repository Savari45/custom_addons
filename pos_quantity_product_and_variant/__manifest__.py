{
    "name": "Point of Sale (POS) - Product and Product Variant Quantity",
    "author": "GRAEF - Productivity Tools",
    "category": "Point of Sale",
    "summary": "Display real-time product and variant stock information at the point of sale. Brings product variants back to the POS screen.",
    "description": """
    # Point of Sale (POS) - Product and Product Variant Quantity
    
    This module enhances your Point of Sale interface by displaying real-time product stock information directly on the product screen.
    
    ## Features
    
    * Display on-hand quantity and virtual quantity of products in POS interface
    * Display product variant quantities with quick-button
    * Show forecasted quantity for better inventory planning
    * Prevent selling out-of-stock items
    """,
    "version": "18.0.2.0.0",
    "depends": ["point_of_sale"],
    "application": True,
    "data": [
        'views/res_config_settings.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            "pos_quantity_product_and_variant/static/src/js/payment_screen.js",
            "pos_quantity_product_and_variant/static/src/js/pos_store.js",
            "pos_quantity_product_and_variant/static/src/js/product_card.js",
            "pos_quantity_product_and_variant/static/src/js/product_screen.js",
            "pos_quantity_product_and_variant/static/src/xml/product_card.xml",
        ],
    },
    "auto_install": False,
    "installable": True,
    "price": 0,
    "currency": "EUR",
    "license": "OPL-1",
    "images": ["static/description/pos_quantity_product_and_variant_cover.png"],

}
