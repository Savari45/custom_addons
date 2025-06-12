{
    'name': 'Public Library Management',
    'version': '1.0',
    'summary': 'Manage public library operations',
    'license': 'LGPL-3',
    'description': """
        This module helps manage public library operations including
        book catalog, members, loans, and returns.
        """,
    'author': 'Alan technologies',
    'website': 'https://alantechnologies.in/',
    'category': 'Services/Library',
    'depends': ['base', 'mail', 'barcodes', 'web'],
    'data': [
        'security/library_security.xml',
        'security/ir.model.access.csv',
        'data/library_data.xml',
        'views/library_book_views.xml',
        'views/library_member_views.xml',
        'views/library_book_category_views.xml',
        'views/library_transaction_views.xml',
        'views/menu_views.xml',
        'reports/book_report.xml',
        'reports/member_report.xml',
        'reports/transaction_report.xml',
        'data/mail_templates.xml',
        'data/cron_jobs.xml',
        'data/ir_sequence_data.xml',
        'wizard/renew_membership_views.xml',
        'wizard/barcode_scanner_wizard_views.xml'
    ],
    'demo': [],
    'assets': {
        'web.report_assets_pdf': [
            'alan_library_management/static/src/css/transaction_report.css',
        ],
        'web.report_assets_common': [
            'alan_library_management/static/src/css/report_styles.css',
            'alan_library_management/static/src/css/member_report.css',
        ],
        'web.assets_backend': [
            'alan_library_management/static/src/css/library.css',
            'alan_library_management/static/src/js/barcode_scanner.js',
            'alan_library_management/static/src/xml/barcode_scanner.xml',
        ],
    },
    'images': ['static/description/banner.gif'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
