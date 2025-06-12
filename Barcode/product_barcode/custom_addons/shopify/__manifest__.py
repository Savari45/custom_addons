{
    "name": "shopify_Tutorial",
    "version": "17.0.0.0.2",
    "summary": "owl",
    "license": "LGPL-3",
    "category": "Other",
    "depends": [
        "base",
        "sale_management",
        "account",
        "stock",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/data.xml",
        "views/views.xml",
        "views/shopify_instance_views.xml",
        "views/inventory_inherit.xml",
        "views/dashboard.xml",  # your ir.actions.client + menuitem
        "views/sale_order_line.xml",  # your ir.actions.client + menuitem
    ],
    # in __manifest__.py
    # in __manifest__.py
    "author": "Synodica Solutions Pvt. Ltd.",
    "website": "https://synodica.com",
    "maintainer": "Synodica Solutions Pvt. Ltd.",
    "support": "support@synodica.com",
    "installable": True,
    "application": True,
    "auto_install": False,
}
