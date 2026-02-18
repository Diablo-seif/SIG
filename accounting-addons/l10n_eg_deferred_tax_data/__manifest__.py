# pylint: skip-file
{
    'name': 'Egyptian Deferred Tax Data',
    'summary': 'Egyptian Deferred Tax Data',
    'author': "Eslam Abdelmaaboud, CORE B.P.O",
    'website': "http://www.core-bpo.com",
    'category': 'Localization',
    # 'version': '0.1.0',
    'license': 'AGPL-3',
    'depends': [
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/deferred_tax_percentage.xml',
        'views/deferred_tax_percentage.xml',
        'views/res_config_settings.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
