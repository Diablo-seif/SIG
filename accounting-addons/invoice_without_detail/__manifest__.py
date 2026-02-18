# pylint: skip-file
{
    'name': 'Invoice Report Without Details',
    'summary': 'Invoice Report Without Details',
    'author': 'Abdalla Mohamed, CORE B.P.O',
    'website': 'http://www.core-bpo.com',
    # 'version': '0.1.0',
    'category': 'Account',
    'license': 'AGPL-3',
    'depends': [
        'account',
    ],
    'data': [
        'report/account_report.xml',
        'report/account_invoice.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
