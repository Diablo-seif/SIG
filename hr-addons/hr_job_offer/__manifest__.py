# pylint: skip-file
{
    'name': 'HR Job Offer',
    'summary': 'HR Job Offer',
    'author': "Muhamed Abd El-Rhman, CORE B.P.O",
    'website': "http://www.core-bpo.com",
    # 'version': '1.0.0',
    'category': 'Human Resources',
    'license': 'AGPL-3',
    'depends': [
        'hr_recruitment',
        'hr_job_position',
        'action_reason',
    ],
    'data': [
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'wizard/job_offer_reject.xml',
        'views/hr_job_offer.xml',
        'views/hr_applicant.xml',
        'views/res_users.xml',
        'views/action_reason.xml',
        'reports/report_layout.xml',
        'reports/job_offer_report.xml',
        'data/ir_sequence.xml',
        'data/mail_template.xml',
    ],
    'demo': [
        'demo/res_users.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
