# pylint: skip-file
{
    'name': "Hr Calendar Time Off Category",
    'summary': "Auto Calendar Create Time Off with Timeoff category",
    'author': "CORE B.P.O",
    'maintainer': 'Abdalla Mohamed',
    'website': "http://www.core-bpo.com",
    'support': 'apps@core-bpo.com',
    'category': 'Human Resources',
    # 'version': '1.0.0',
    'license': 'OPL-1',
    'depends': [
        'hr_calendar_leave',
        'hr_leaves_holidays',
    ],
    'installable': True,
    'auto_install': True,
    'application': False,
}
