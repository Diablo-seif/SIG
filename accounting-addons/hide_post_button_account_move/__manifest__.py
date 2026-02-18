# pylint: disable=skip-file
{
    'name': 'Hide Post Button Account Move',
    'summary': 'Hide Post Button Account Move',
    'author': "Mohamed Osama, CORE B.P.O",
    'website': "http://www.core-bpo.com",
    'category': 'Accounting',
    'depends': [
        'account',
    ],
    'data': [
        'security/security.xml',
        'views/account_move.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
