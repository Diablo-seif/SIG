# pylint: disable=missing-docstring, manifest-required-author
{
    'name': "Hr Demo Users",
    'summary': "Hr Demo Users",
    'author': 'Hashem Aly, CORE B.P.O',
    'website': 'http://www.core-bpo.com',
    # 'version': '13.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'hr_contract',
    ],
    'data': [
    ],
    'demo': [
        'demo/res_partner.xml',
        'demo/res_users.xml',
        'demo/department_employee.xml',
        'demo/hr_contract.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
