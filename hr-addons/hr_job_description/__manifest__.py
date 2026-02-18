# pylint: skip-file
{
    'name': 'HR Job Description',
    'summary': 'HR Job Description',
    'author': "Muhamed Abd El-Rhman, CORE B.P.O",
    'website': "http://www.core-bpo.com",
    # 'version': '1.0.0',
    'category': 'Human Resources',
    'license': 'AGPL-3',
    'depends': [
        'website_hr_recruitment',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_job_description_template.xml',
        'views/hr_job.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
