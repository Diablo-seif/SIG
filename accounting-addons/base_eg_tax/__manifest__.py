# pylint: skip-file
{
    'name': 'Egypt - Base Tax Data',
    'summary': 'Egypt - Base Tax Data',
    'author': "Eslam Abdelmaaboud, CORE B.P.O",
    'website': "http://www.core-bpo.com",
    'category': 'Localization',
    # 'version': '0.1.0',
    'license': 'AGPL-3',
    'depends': [
        'account',
    ],
    'data': [
        'views/account_journal.xml',
        'views/account_tax.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
