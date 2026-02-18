# pylint: skip-file
{
    'name': 'User Signature',
    'summary': 'User Signature',
    'author': "Muhamed Abd El-Rhman, CORE B.P.O",
    'website': "http://www.core-bpo.com",
    # 'version': '1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'hr_job_offer',
        'sign'
    ],
    'data': [
        'views/res_users.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
}
