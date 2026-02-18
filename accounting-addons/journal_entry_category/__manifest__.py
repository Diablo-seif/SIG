# pylint: skip-file
{
    'name': 'Journal Entry Category',
    'summary': 'Journal Entry Category',
    'author': "CORE B.P.O",
    'maintainer': "Muhamed Abd El-Rhman, Abdalla Mohamed",
    'website': "http://www.core-bpo.com",
    # 'version': '1.0.0',
    'category': 'Accounting/Accounting',
    'license': 'OPL-1',
    'depends': [
        'account',
    ],
    'data': [
        'views/account_move.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'uninstall_hook': 'uninstall_hook',
}
