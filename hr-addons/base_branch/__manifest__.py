# pylint: skip-file
{
    'name': "Base Branch",
    'summary': "Base Branch",
    'author': "Hashem Aly, CORE B.P.O",
    'website': "http://www.core-bpo.com",
    'category': 'Base',
    # 'version': '1.1.0',
    'license': 'AGPL-3',
    'depends': [
        'contacts',
    ],
    'data': [
        'security/ir_rule.xml',
        'security/ir.model.access.csv',
        'views/hr_branch.xml',
        'views/hr_branch_tag.xml',
        'views/res_users.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
