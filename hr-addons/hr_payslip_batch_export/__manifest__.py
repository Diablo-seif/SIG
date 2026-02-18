# pylint: skip-file
{
    'name': "Payslips Batch Export Excel File",
    'summary': "Payslips Batch Export Excel File",
    'author': "Hashem Aly, CORE B.P.O",
    'website': "http://www.core-bpo.com",
    'category': 'Human Resourses',
    # 'version': '1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'hr_payroll',
    ],
    'data': [
        'views/hr_payslip_run.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'external_dependencies': {
        'python': ['xlwt']
    },
}
