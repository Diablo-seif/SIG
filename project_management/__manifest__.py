# pylint: disable=skip-file
{
    'name': 'Project Management',
    'summary': 'Project Management',
    'author': "Muhamed Abd El-Rhman, CORE B.P.O",
    'website': "http://www.core-bpo.com",
    'sequence': 1,
    # 'version': '1.0.1',
    'depends': [
        'project',
        'hr_timesheet',
    ],
    'data': [
        # 'security/security.xml',
        'security/ir.model.access.csv',
        'views/project.xml',
        'views/project_task.xml',
        'views/project_plan_line.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
