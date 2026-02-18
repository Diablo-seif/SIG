# pylint: skip-file
{
    'name': 'HR Create Employee From Applicant',
    'summary': 'Create Employee From Applicant',
    'author': "Yousef Soliman, CORE B.P.O",
    'website': "http://www.core-bpo.com",
    # 'version': '1.0.0',
    'category': 'Human Resources',
    'license': 'AGPL-3',
    'depends': [
        'hr_contract_type',
        'hr_job_offer'
    ],
    'data': [
        'views/hr_employee_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
