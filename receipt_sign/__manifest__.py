{
    "name": "POS Receipt Signature Code",
    "version": "1.0",
    "depends": ["point_of_sale",'account'],
    "category": "Point of Sale",
    "assets": {
        "point_of_sale._assets_pos": [
            # "receipt_sign/static/src/js/pos_store.js",
            # "receipt_sign/static/src/js/customorderreceipt.js",
            #
            # "receipt_sign/static/src/js/print.js",
            # "receipt_sign/static/src/js/reprintreceiptscreen.js",
            "receipt_sign/static/src/xml/customreceipt.xml",
        ],
    },
    "installable": True,
    "application": False,
}
