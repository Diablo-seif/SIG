# pylint: skip-file
{
    'name': 'Egyptian Symbiotic Contribution',
    'summary': 'Egyptian Symbiotic Contribution',
    'author': "Hassan Ibrahim Ali, CORE B.P.O",
    'website': "http://www.core-bpo.com",
    'category': 'Localization',
    # 'version': '0.1.0',
    'license': 'AGPL-3',
    'depends': [
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings.xml',
        'views/symbiotic_contribution .xml',
        'wizards/symbiotic_contribution_computation.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
