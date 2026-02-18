# pylint: disable=missing-docstring, manifest-required-author
{
    'name': 'Egyptian Tax Included In Price',
    'summary': 'Egyptian VAT Taxation',
    'author': "Hassan Ibrahim Ali, CORE B.P.O",
    'website': "http://www.core-bpo.com",
    'category': 'Localization',
    # 'version': '0.1.0',
    'license': 'AGPL-3',
    'depends': [
        'account',
        'account_tax_group_type',
    ],
    'data': [
        'views/res_config_settings.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
