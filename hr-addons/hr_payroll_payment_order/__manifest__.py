# pylint: skip-file
{
    'name': "Hr Payroll Payment Order",
    'summary': "Hr Payroll Payment",
    'author': "CORE B.P.O",
    'maintainer': "Abdalla Mohamed",
    'website': "http://www.core-bpo.com",
    'category': 'payroll',
    # 'version': '1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'hr_payroll',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'wizard/hr_payslip_payment_allocate.xml',
        'views/hr_payslip_payment_method.xml',
        'views/hr_payslip.xml',
        'views/hr_payslip_run.xml',
        'views/hr_payslip_payment_order.xml',
        'data/ir_sequence.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
