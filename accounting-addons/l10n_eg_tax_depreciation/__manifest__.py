# pylint: skip-file
{
    'name': 'Egyptian Taxes Depreciation',
    'summary': 'Egyptian Taxes Depreciation',
    'author': "Hassan Ibrahim Ali, CORE B.P.O",
    'website': "http://www.core-bpo.com",
    'category': 'Localization',
    # 'version': '0.1.0',
    'license': 'AGPL-3',
    'depends': [
        'l10n_eg_deferred_tax_data',
    ],
    'data': [
        'data/tax_depreciation_category.xml',
        'security/ir.model.access.csv',
        'views/tax_depreciation_category.xml',
        'wizards/compute_tax_depreciation.xml',
        'views/tax_depreciation_computation.xml',
        'views/res_config_settings.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
