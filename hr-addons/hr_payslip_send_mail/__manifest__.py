
# pylint: disable=missing-docstring, manifest-version-format
# pylint: disable=manifest-required-author
{
    'name': "Hr Payslips Send Mail",
    'summary': "Hr Payslips Send Mail Form Template",
    'author': "Hashem Aly, CORE B.P.O",
    'website': "http://www.core-bpo.com",
    'category': 'payroll',
    # 'version': '13.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'hr_payroll',
        'queue_job',
    ],
    'data': [
        'views/hr_payslip.xml',
        'views/hr_payslip_run.xml',
        'data/payslip_mail_template.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
