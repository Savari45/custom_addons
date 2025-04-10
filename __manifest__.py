{
    'name': "Hospital Management",
    'description': """
        Hospital management module which is used to mange the hospital functionalities prescription,patient,doctor diagnosis etc
    """,
    'summary': """
    Hospital management module which is used to mange the hospital functionalities prescription,patient,doctor diagnosis etc
""",
    'author': "Alan Technologies",
    'company': "Alan Technologies",
    'maintainer': 'Alan Technologies',
    'website': "https://www.alantech.com",
    "license": "AGPL-3",
    'category': 'Hospital',
    'version': '18.0.1.0.0',
    'depends': ['base', 'hr', 'account', 'sale', 'product', 'web'],
    'data': [
        'data/patient_id_sequence.xml',
        'data/dental_specialist_data.xml',
        'data/dental_treatment_data.xml',
        'data/dental_time_shift_data.xml',
        'data/medicine_frequency_data.xml',
        'data/treatment_category_data.xml',
        'views/patient_view.xml',
        'views/dental_appointment_views.xml',
        'views/dental_doctor_views.xml',
        'views/dental_prescription_views.xml',
        # 'views/doctor_views.xml',
        # 'views/dental_purpose_views.xml',
        'views/teeth_chart_views.xml',
        'views/dental_treatment_views.xml',
        'views/treatment_category_views.xml',
        'views/medicine_frequency_views.xml',
        'views/dental_medicine_views.xml',
        # 'views/assets.xml',
        'views/medical_questions_views.xml',
        'views/dental_doctor_views.xml',
        'views/dental_specialist_views.xml',
        'views/dental_time_shift_views.xml',
        'report/dental_prescription_report.xml',
        'report/dental_prescription_templates.xml',
        # 'wizard/xray_report_views.xml',
        'security/ir.model.access.csv'
    ],

    'installable': True,
    'auto_install': False,
    'application': True,

}
