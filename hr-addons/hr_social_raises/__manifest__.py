# pylint: disable=missing-docstring,manifest-required-author
{
    'name': 'HR Social Raises',
    'summary': 'HR Social Raises',
    'author': "Muhamed Abd El-Rhman, CORE B.P.O",
    'website': "http://www.core-bpo.com",
    # 'version': '1.0.0',
    'category': 'Human Resources',
    'license': 'AGPL-3',
    'depends': [
        'hr_employee_insurance',
    ],
    'data': [
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'views/hr_employee.xml',
        'wizard/apply_raise.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
