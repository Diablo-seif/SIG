# pylint: skip-file
{
    'name': 'Integrate USB Token with E-Invoice',
    'summary': 'Expose APIs used in USB token',
    'author': 'CORE B.P.O',
    'maintainer': 'Abdalla MOhamed',
    'website': 'http://www.core-bpo.com',
    'support': 'apps@core-bpo.com',
    'category': 'Localization',
    # # 'version': '16.0.1.0.0',
    'license': 'OPL-1',
    'depends': [
        'l10n_eg_einvoice',
        'auth_api_key',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/account_einvoice_token_log.xml',
    ],

    'installable': True,
    'auto_install': False,
    'application': False,
}
