{
    'name': 'Hospital Management System',
    'version': '1.0',
    'summary': 'Manage hospital patients',
    'depends': ['base', 'mail'],
    'data': [
        'views/hms_patient_views.xml',
        'views/hms_department_views.xml',
        'views/hms_doctors_views.xml',
        'views/hms_menu.xml',
    ],
    'installable': True,
    'application': True,
}