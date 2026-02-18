# pylint: skip-file
{
    'name': 'Set Password on Email Document',
    'summary': 'Easily protect the template attachment (PDF/Excel)',
    'author': "Hashem Aly, CORE B.P.O",
    'website': "http://www.core-bpo.com",
    # 'version': '1.0.0',
    'category': 'email',
    'license': 'AGPL-3',
    'depends': [
        'mail',
    ],
    'data': [
        'views/mail_template.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
