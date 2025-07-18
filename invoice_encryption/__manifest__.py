{
    'name': "Invoice Encryption",
    'summary': "Display only in-stock products in sale order lines and show available on-hand quantity.",
    'description': """
        
    """,
    'version': '18.0.1.0.0',
    'category': 'Sales',
    'author': 'Alan Technologies',
    'maintainer': 'Alan Technologies',
    'company': 'Alan Technologies',
    'website': "https://alantechnologies.in/",
    'license': "AGPL-3",
    'depends': ['base', 'sale', 'account'],
    'data': [
        'data/automation_rule.xml',
        'security/ir.model.access.csv',
        'security/report_encryption_rules.xml',
        'security/report_encryption_security.xml',
        'views/encryption_views.xml',
        'views/res_users_views.xml',
        'report/inherit_invoice.xml',
        'views/signature_verifier_view.xml',
        # 'views/inherit_account_views.xml',

    ],
    'images': ['static/description/banner.gif'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'sequence': 1,
}
