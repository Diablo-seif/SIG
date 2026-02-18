# pylint: skip-file
{
    'name': 'Egyptian Deduction Taxes',
    'summary': 'Enable Egyptian Deduction Taxes Calculations',
    'author': "Eslam Abdelmaaboud, CORE B.P.O",
    'website': "http://www.core-bpo.com",
    'category': 'Localization',
    # 'version': '0.1.0',
    'license': 'AGPL-3',
    'depends': [
        'base_eg_tax',
        'partner_legal_information',
        'fiscal_position_dates',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner.xml',
        'views/product_template.xml',
        'views/account_move.xml',
        'views/account_move_line.xml',
        'views/account_payment.xml',
        'views/account_fiscal_position.xml',
        'wizard/deduction_register_payment.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
