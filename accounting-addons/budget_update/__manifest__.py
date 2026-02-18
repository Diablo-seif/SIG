# pylint: skip-file
{
    'name': 'Budget Update',
    'summary': 'Budget Update',
    'author': "Muhamed Abd El-Rhman, CORE B.P.O",
    'website': "http://www.core-bpo.com",
    # 'version': '0.1.0',
    'category': 'Accounting/Accounting',
    'license': 'AGPL-3',
    'depends': [
        'account_budget',
    ],
    'data': [
        'views/crossovered_budget.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
