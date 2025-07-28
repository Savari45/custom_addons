{
    "name": "Custom POS receipt",
    "summary": """
        Custom POS receipt for Restaurant.
    """,
    "description": """
        Custom POS receipt for Restaurant.
    """,
    
    'author': "Jony Ghosh",
    
    "category": "Tools",
    "version": "18.0.0.1",
    "license": "OPL-1",


    "depends": ['base', 'point_of_sale', 'barcodes'],
    "assets": {
        "point_of_sale._assets_pos": [
            "/pos_receipt_custom/static/src/**/*",
        ],
    },
    
    "images": [
        "static/description/icon.png",
    ],
    
    
    "application": True,
    "installable": True,
    "auto_install": False,
    
    "maintainer": "Jony Ghosh",
    "support": "jony.ghosh98@gmail.com",
}
