# pylint: disable=skip-file
{
    'name': 'SIG Department Budget',
    'summary': 'SIG Department Budget',
    'author': "Mohamed Osama, CORE B.P.O",
    'website': "http://www.core-bpo.com",
    'sequence': 1,
    'depends': [
        'base',
        'hr', 
        'proposal'
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/hr_department.xml',
        'views/department_budget_line.xml',
        'views/department_menu.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
