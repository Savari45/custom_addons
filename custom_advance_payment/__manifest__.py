{
    'name': 'Custom Advance Payment with Approval & Reconciliation',
    'version': '1.0',
    'category': 'Accounting',
    'summary': 'Enhance Advance Payments in Purchase Orders with approval and reconciliation.',
    'depends': ['purchase', 'account', 'mail','approvals','base'],
    'data': [
        'security/ir.model.access.csv',
        'views/purchase_order_view.xml',
        'views/account_payment_view.xml',
       # 'data/approval_rules.xml',
        'reports/advance_payment_report.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
