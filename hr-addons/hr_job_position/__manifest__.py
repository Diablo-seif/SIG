# pylint: skip-file
{
    'name': 'HR Job Position',
    'summary': 'HR Job Position',
    'author': "Muhamed Abd El-Rhman, CORE B.P.O",
    'website': "http://www.core-bpo.com",
    # 'version': '1.0.0',
    'category': 'Human Resources',
    'license': 'AGPL-3',
    'depends': [
        'hr_recruitment',
        'hr_contract_type',
        'hr_organization_levelling',
    ],
    'data': [
        'views/hr_job.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
