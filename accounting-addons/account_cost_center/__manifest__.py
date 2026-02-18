# pylint: skip-file
{
    'name': 'Cost center',
    'summary': 'Cost center Module',
    'author': "Hashem ALy, CORE B.P.O",
    'website': "http://www.core-bpo.com",
    'category': 'Accounting',
    # 'version': '0.1.0',
    'license': 'AGPL-3',
    'depends': [
        'account',
        'account_accountant',
        'base_view_inheritance_extension'
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/account_cost_center_security.xml',
        'views/account_cost_center.xml',
        'views/account_move.xml',
        'views/account_move_line.xml',
        'views/account_invoice_report.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
