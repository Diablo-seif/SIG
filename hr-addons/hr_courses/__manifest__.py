# pylint: skip-file
{
    'name': 'HR Courses',
    'summary': 'HR Courses',
    'author': "Yousef Soliman, CORE B.P.O",
    'website': "http://www.core-bpo.com",
    # 'version': '1.0.0',
    'category': 'Human Resources',
    'license': 'AGPL-3',
    'depends': [
        'hr_skills',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_course.xml',
        'views/hr_course_type.xml',
        'views/hr_job.xml'
    ],
    'demo': [
        'demo/hr_course_type.xml',
        'demo/hr_course.xml',
        'demo/hr_course_provider_line.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
