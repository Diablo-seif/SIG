# pylint: skip-file
{
    'name': 'Payment Request',
    'summary': 'Payment Request',
    'author': "Muhamed Abd El-Rhman, CORE B.P.O",
    'website': "http://www.core-bpo.com",
    # 'version': '0.1.0',
    'category': 'Accounting/Payment',
    'license': 'AGPL-3',
    'depends': [
        'account',
    ],
    'data': [
        'security/ir_rule.xml',
        'security/ir.model.access.csv',
        'views/payment_request_line.xml',
        'views/payment_request.xml',
        'views/res_config_settings.xml',
        'data/ir_sequence.xml',
        'data/ir_actions_server.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
