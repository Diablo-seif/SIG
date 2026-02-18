# pylint: skip-file
{
    'name': "HR Branch",
    'summary': "HR Branch",
    'author': "Hashem Aly, CORE B.P.O",
    'website': "http://www.core-bpo.com",
    'category': 'Human Resources',
    # 'version': '1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'base_branch',
        'hr',
    ],
    'data': [
        'views/hr_employee.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
