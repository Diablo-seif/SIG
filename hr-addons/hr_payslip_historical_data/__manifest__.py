# pylint: skip-file
{
    'name': "HR Payslip Historical Data",
    'summary': "HR Payslip Historical Data For Output Payslip Values",
    'author': "Eslam Abdelmaaboud, CORE B.P.O",
    'website': "http://www.core-bpo.com",
    'category': 'Human Resources',
    # 'version': '1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'hr_payroll',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_payslip_historical_data.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
