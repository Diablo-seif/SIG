# pylint: skip-file
{
    'name': 'Egyptian Deduction Tax Report',
    'summary': 'Egyptian Deduction Tax Report',
    'author': "Eslam Abdelmaaboud, CORE B.P.O",
    'website': "http://www.core-bpo.com",
    'category': 'Localization',
    # 'version': '0.1.0',
    'license': 'AGPL-3',
    'depends': [
        'l10n_eg_deduction_tax',
    ],
    'data': [
        'security/ir.model.access.csv',
        'report/deduction_line_report.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
