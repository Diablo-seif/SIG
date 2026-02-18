# pylint: skip-file
{
    'name': 'Salary Input',
    'summary': 'Salary Input for Salary Rules',
    'author': "Abdalla Mohamed, CORE B.P.O",
    'website': "http://www.core-bpo.com",
    'category': 'Human Resources',
    # 'version': '1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'hr_payroll',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/salary_input.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
