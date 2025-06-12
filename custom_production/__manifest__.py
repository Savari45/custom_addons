{
    'name': 'MRP Dynamic Component Edit',
    'version': '1.0',
    'depends': ['mrp'],
    'author': 'Your Name',
    'category': 'Manufacturing',
    'description': 'Allows editing components during production before final produce.',
    'data': [
        'views/mrp_production_view.xml',
        'views/mrp_reverse_production.xml',
    ],
    'installable': True,
    'auto_install': False,
}
