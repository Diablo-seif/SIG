# pylint: skip-file
{
    'name': 'Fiscal Postiion Dates',
    'summary': 'Fiscal Position Filtered By Dates',
    'author': "Hashem Aly, CORE B.P.O",
    'website': "http://www.core-bpo.com",
    'category': 'account',
    # 'version': '0.1.0',
    'license': 'AGPL-3',
    'depends': [
        'account',
    ],
    'data': [
        'views/account_fiscal_position.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
