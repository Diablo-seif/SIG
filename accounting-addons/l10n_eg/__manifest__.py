# pylint: disable=missing-docstring, manifest-required-author
{
    'name': 'Egypt - Accounting',
    'summary': 'Egyptian Accounting Localization',
    'author': "Eslam Abdelmaaboud, CORE B.P.O",
    'website': "http://www.core-bpo.com",
    'category': 'Localization',
    # 'version': '0.1.0',
    'license': 'AGPL-3',
    'depends': [
        'base_eg_tax',
        'account_tax_group_type',
    ],
    'data': [
        'data/l10n_eg_coa.xml',
        'data/account.account.template.csv',
        'data/account_tax_template.xml',
        'data/res_country_groups.xml',
        'data/account_fiscal_position.xml',
        'data/l10n_eg_coa_post.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
