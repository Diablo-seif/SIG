# pylint: skip-file
{
    'name': 'Action Reason',
    'summary': 'Action Reason',
    'author': "Muhamed Abd El-Rhman, CORE B.P.O",
    'website': "http://www.core-bpo.com",
    # 'version': '1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'base',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/action_reason.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
