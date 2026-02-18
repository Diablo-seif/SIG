{
    'name': 'Employee Overtime Type',
    # 'version': '1.0.0',
    'summary': 'Employee Overtime Type',
    'category': 'Human Resources/Overtime',
    'author': 'CORE B.P.O',
    'maintainer': 'Younis Mostafa Khalaf',
    'website': 'http://www.core-bpo.com',
    'license': 'AGPL-3',
    'depends': [
        'aspl_hr_overtime_ee',
        'hr_holidays',
        'base',
    ],
    'data': [
        'views/res_settings.xml',
        'views/hr_employee_overtime.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
# pylint: disable=missing-docstring,manifest-required-author
