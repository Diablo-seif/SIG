# pylint: skip-file
{
    'name': 'HR Allocation Configuration',
    'summary': 'HR Allocation Configuration',
    'author': "Muhamed Abd El-Rhman, CORE B.P.O",
    'website': "http://www.core-bpo.com",
    # 'version': '1.0.0',
    'category': 'Human Resources',
    'license': 'AGPL-3',
    'depends': [
        'hr_holidays',
        'hr_employee_insurance',
    ],
    'data': [
        'views/res_config_settings.xml',
        'views/hr_employee.xml',
        'data/ir.cron.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
