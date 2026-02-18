# pylint: skip-file
{
    'name': 'HR Salary Adjustment',
    'summary': 'HR Salary Adjustment',
    'author': "Muhamed Abd El-Rhman, CORE B.P.O",
    'website': "http://www.core-bpo.com",
    # 'version': '1.0.0',
    'category': 'Human Resourses',
    'license': 'AGPL-3',
    'depends': [
        'hr_salary_tax'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_actions_server.xml',
        'views/hr_salary_rule.xml',
        'wizard/salary_adjustment.xml',
        'report/salary_adjustment.xml',
        'report/reports.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
