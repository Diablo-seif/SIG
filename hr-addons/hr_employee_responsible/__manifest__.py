# pylint: skip-file
{
    'name': 'HR Employee Responsible',
    'summary': 'HR Employee Responsible',
    'author': "Muhamed Abd El-Rhman, CORE B.P.O",
    'website': "http://www.core-bpo.com",
    # 'version': '1.0.0',
    'category': 'Human Resources',
    'license': 'AGPL-3',
    'depends': [
        'hr',
    ],
    'data': [
        'views/hr_employee.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
