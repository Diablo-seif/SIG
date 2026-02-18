# pylint: disable=missing-docstring, manifest-required-author
{
    'name': 'Egyptian Income Tax',
    'summary': 'Egyptian Income Tax',
    'author': "Eslam Abdelmaaboud, CORE B.P.O",
    'website': "http://www.core-bpo.com",
    'category': 'Localization',
    # 'version': '0.1.0',
    'license': 'AGPL-3',
    'depends': [
        'l10n_eg_deferred_tax_data',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizards/income_tax_wizard.xml',
        'views/income_tax_line.xml',
        'views/res_config_settings.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
