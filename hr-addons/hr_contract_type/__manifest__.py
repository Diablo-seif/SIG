# pylint: skip-file
{
    'name': 'HR Contract Type',
    'summary': 'HR Contract Type',
    'author': "Muhamed Abd El-Rhman, CORE B.P.O",
    'website': "http://www.core-bpo.com",
    # 'version': '1.0.0',
    'category': 'Human Resources',
    'license': 'AGPL-3',
    'depends': [
        'hr_contract'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_contract_type.xml',
        'data/hr_contract_type.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
}
