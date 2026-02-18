# pylint: skip-file
{
    'name': 'Dynamic Approval',
    'summary': 'Dynamic Approval',
    'author': "Muhamed Abd El-Rhman, CORE B.P.O",
    'website': "http://www.core-bpo.com",
    # 'version': '1.0.0',
    'category': 'Human Resources/Approvals',
    'license': 'AGPL-3',
    'depends': [
        'approvals',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/approval_category.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
}
