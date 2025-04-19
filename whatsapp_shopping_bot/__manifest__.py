{
    'name': 'WhatsApp Shopping Bot',
    'version': '1.0',
    'author': 'Your Name',
    'category': 'Sales',
    'summary': 'A WhatsApp chatbot to browse products and create Sale Orders in Odoo',
    'depends': ['base', 'sale', 'product'],
    'data': [
       # 'security/ir.model.access.csv',
        'views/bot_session_views.xml',
    ],
    'installable': True,
    'application': True,
}
