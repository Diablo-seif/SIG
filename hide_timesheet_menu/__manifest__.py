# pylint: disable=skip-file
{
    'name': 'Hide Timesheet Menu',
    'summary': 'Hide Timesheet Menu',
    'author': "Mohamed Osama, CORE B.P.O",
    'website': "http://www.core-bpo.com",
    'sequence': 1,
    # 'version': '1.0.0',
    'depends': [
        'hr_timesheet',
    ],
    'data': [
        'security/security.xml',
        'views/ir_ui_menu.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
