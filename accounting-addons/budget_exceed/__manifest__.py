# pylint: skip-file
{
    'name': 'Budget Exceed',
    'summary': 'Budget Exceed',
    'author': "Muhamed Abd El-Rhman, CORE B.P.O",
    'website': "http://www.core-bpo.com",
    # 'version': '0.1.0',
    'category': '',
    'license': 'AGPL-3',
    'depends': [
        'account_budget',
    ],
    'data': [
        'data/ir_cron.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
