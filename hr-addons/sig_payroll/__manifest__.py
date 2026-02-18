# pylint: disable=skip-file
{
    'name': 'SIG Payroll',
    'summary': 'SIG Payroll',
    'author': "Mohamed Osama, CORE B.P.O",
    'website': "http://www.core-bpo.com",
    'sequence': 1,
    'depends': [
        'hr',
        'hr_payroll',
        'extra_employee_info',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/hr_payroll_deduction.xml',
        'views/hr_payslip.xml',
        'views/hr_payslip_run.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
