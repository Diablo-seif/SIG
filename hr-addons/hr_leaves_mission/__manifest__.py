# pylint: skip-file
{
    'name': "Hr Leave Missions ",
    'summary': "Manage Missions",
    'author': "Eslam Abdelmaaboud, CORE B.P.O",
    'website': "http://www.core-bpo.com",
    'category': 'Human Resources',
    # # 'version': '16.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'hr_leaves_holidays',
    ],
    'data': [
        'views/hr_leave.xml',
        'data/hr_holidays_data.xml',
    ],
    'demo': [

    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
