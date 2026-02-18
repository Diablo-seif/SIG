# pylint: skip-file
{
    'name': 'Training Needs Assessment Execution',
    'summary': 'Training Needs Assessment Execution',
    'author': "Muhamed Abd El-Rhman, CORE B.P.O",
    'website': "http://www.core-bpo.com",
    # 'version': '1.0.0',
    'category': 'Human Resources',
    'license': 'AGPL-3',
    'depends': [
        'hr_tna',
        'hr_holidays',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_tna_courses.xml',
        'wizard/tna_course_execution.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
