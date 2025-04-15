{
    'name': 'Hospital Management System',
    'version': '1.0',
    'summary': 'Manage hospital patients',
    'depends': ['base', 'mail', 'crm'],
    'data': [
        'security/hms_security.xml',
        'security/ir.model.access.csv',
        'views/hms_patient_views.xml',
        'views/hms_department_views.xml',
        'views/hms_doctors_views.xml',
        'views/hms_menu.xml',
        'views/res_partner_views.xml',
        'reports/patient_report.xml',
    ],
    'installable': True,
    'application': True,
}