{
    'name': 'Central System Integration',
    'summary': 'Central System Integration',
    'author': "Mohamed Osama, CORE B.P.O",
    'website': "http://www.core-bpo.com",
    # 'version': '1.0.7',
    'license': 'AGPL-3',
    'sequence': 1,
    'depends': [
        'base_setup',
        'account', 
        'partner_legal_information',
        'project'
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/account_account.xml",
        "views/project_project_views.xml",
        "views/res_config_settings.xml",
        "views/res_partner_views.xml",
        "wizards/token_wizard.xml"
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
