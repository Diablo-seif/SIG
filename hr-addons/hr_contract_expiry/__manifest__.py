# pylint: skip-file
{
    'name': 'HR Contract Expiry Date',
    'summary': 'Mark Contract Expiry Date',
    'author': "Hashem Aly, CORE B.P.O",
    'website': "http://www.core-bpo.com",
    'category': 'Human Resources',
    # 'version': '1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'hr_contract',
    ],
    'data': [
        'views/hr_contract.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
