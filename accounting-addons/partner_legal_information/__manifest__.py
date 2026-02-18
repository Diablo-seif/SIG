# pylint: skip-file
{
    'name': 'Partner Legal Information',
    'summary': 'Partner Legal Information',
    'author': 'Eslam Abdelmaaboud, CORE B.P.O',
    'website': 'http://www.core-bpo.com',
    # 'version': '0.1.0',
    'category': 'Localization',
    'license': 'AGPL-3',
    'depends': [
        'account',
    ],
    'data': [
        'data/vat.department.csv',
        'security/ir.model.access.csv',
        'views/legal_entity_type.xml',
        'views/res_partner.xml',
        'views/vat_department.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
