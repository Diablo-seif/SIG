# pylint: disable=missing-docstring,manifest-required-author
{
    'name': 'HR Allocation Calculation',
    'summary': 'HR Allocation Calculation',
    'author': "Yousef Soliman, CORE B.P.O",
    'website': "http://www.core-bpo.com",
    # 'version': '13.0.1.0.0',
    'category': 'Human Resources',
    'license': 'AGPL-3',
    'depends': [
        'hr_holidays_accrual_advanced',
        'hr_contract',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_leave_type_view.xml',
        'views/hr_leave_allocation.xml',
        'views/hr_employee.xml',
        'views/hr_allocation_tag.xml',
        'data/hr_leave_type.xml',
        'data/hr_allocation_tag.xml',
        'data/hr_leave_type_tag.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
