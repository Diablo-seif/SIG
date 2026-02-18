# pylint: skip-file
{
    'name': 'Budget Report',
    'summary': 'Budget Report',
    'author': "Muhamed Abd El-Rhman, CORE B.P.O",
    'website': "http://www.core-bpo.com",
    # 'version': '0.1.0',
    'category': 'Accounting/Accounting',
    'license': 'AGPL-3',
    'depends': [
        'account_budget',
        'account_reports',
    ],
    'data': [
        'data/ir_actions_client.xml',
        'views/line_template.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
