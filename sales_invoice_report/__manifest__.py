{
    'name': 'Sales Invoice Report',
    'depends': ['base', 'account', 'sale'],
    'data': [
         'security/ir.model.access.csv',
        'wizard/invoice_report_wizard_view.xml',
        'views/menu.xml',
        'reports/invoice_report_template.xml',
        'reports/invoice_report_action.xml',
    ],
    'installable': True,
}
