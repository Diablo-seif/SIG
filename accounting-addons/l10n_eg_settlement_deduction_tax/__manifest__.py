# pylint: skip-file
{
    'name': "Settlement Deduction Tax",
    'summary': "Settlement Deduction Tax",
    'author': "Eslam Abdelmaaboud, CORE B.P.O",
    'website': "http://www.core-bpo.com",
    'category': 'Localization',
    # 'version': '0.1.0',
    'license': 'AGPL-3',
    'depends': [
        'l10n_eg_deduction_tax_report',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_actions_server.xml',
        'wizards/settlement_deduction_tax.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
