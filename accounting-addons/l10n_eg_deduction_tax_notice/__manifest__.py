# pylint: skip-file
{
    'name': 'Egyptian Deduction Taxes Notice',
    'summary': 'Enable Egyptian Deduction Taxes Calculations',
    'author': "Eslam Abdelmaaboud, CORE B.P.O",
    'website': "http://www.core-bpo.com",
    'category': 'Localization',
    # 'version': '0.1.0',
    'license': 'AGPL-3',
    'depends': [
        'l10n_eg_deduction_tax',
    ],
    'data': [
        'report/deduction_tax_report.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
