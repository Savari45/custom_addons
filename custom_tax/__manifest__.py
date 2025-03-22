{
    'name': 'Add the custom taxes',
    'version': '1.0',
    'license': 'LGPL-3',
    'depends': ['base', 'account', 'sale', 'purchase'],
    'data': [
        'data/custom_tax.xml',
        'data/custom_tax_gst_5.xml',
        'data/custom_tax_gst_12.xml',
        'data/custom_tax_gst_28.xml',
    ],
    'installable': True,
    'application': False,
}
