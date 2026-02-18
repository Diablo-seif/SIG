# pylint: disable=skip-file
{
    'name': 'Access Tags',
    'summary': 'Access Tags',
    'author': "Muhamed Abd El-Rhman, CORE B.P.O",
    'website': "http://www.core-bpo.com",
    'sequence': 1,
    'depends': [
        'base',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/res_users.xml',
        'views/access_tags.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
