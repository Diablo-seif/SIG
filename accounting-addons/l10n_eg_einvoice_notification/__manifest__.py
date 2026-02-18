# pylint: skip-file
{
    'name': 'E-Invoice Notifications',
    'summary': 'Expose APIs used to receive notifications from ETA',
    'author': 'CORE B.P.O',
    'maintainer': 'Abdalla MOhamed',
    'website': 'http://www.core-bpo.com',
    'support': 'apps@core-bpo.com',
    'category': 'Localization',
    # 'version': '1.0.0',
    'license': 'OPL-1',
    'depends': [
        'l10n_eg_einvoice',
        'auth_api_key',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/account_einvoice_incoming.xml',
        'views/account_document_receive.xml',
    ],

    'installable': True,
    'auto_install': False,
    'application': False,
}
