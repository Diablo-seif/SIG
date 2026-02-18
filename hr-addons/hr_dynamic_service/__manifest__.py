# pylint: skip-file
{
    'name': "HR Dynamic Approval",
    'summary': "Manage HR Dynamic Approval Requests",
    'author': 'Hashem Aly, CORE B.P.O',
    'website': 'http://www.core-bpo.com',
    # 'version': '1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'hr',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'wizard/hr_dynamic_service_refuse.xml',
        'views/hr_dynamic_service_type.xml',
        'views/hr_dynamic_service_stage.xml',
        'views/hr_dynamic_service.xml',
        'views/hr_dynamic_service_dashboard.xml',
        'views/menuitem.xml',
    ],
    'demo': [
        'demo/hr_dynamic_service.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
