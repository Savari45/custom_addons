{
    "name": "Prevent Negative Stock (POS) Odoo Online, Odoo.sh, On Premise",
    "version": "18.0.0.0.1",
    "license": "OPL-1",
    "author": "Nirav Rathod",
    "website": "https://github.com/niravrathod",
    "category": "Point of Sale",
    "summary": "Prevent adding products with negative stock in POS For Odoo Online, Odoo.sh, On Premise",
    "depends": ["point_of_sale", "web", "stock"],
    "assets": {
        "point_of_sale._assets_pos": [
            "nr_prevent_negative_stock_pos/static/src/js/pos_negative_stock.js"
        ]
    },
    "images": ["static/description/image.gif"],
    "installable": True,
    "auto_install": False,
}
