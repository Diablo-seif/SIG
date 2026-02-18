# pylint: disable=skip-file
{
    'name': 'HR Leave Type Code',
    'summary': 'HR Leave Type Code',
    'author': "Mohamed Osama, CORE B.P.O",
    'website': "http://www.core-bpo.com",
    'sequence': 1,
    'depends': [
        'base',
        'hr_holidays',
    ],
    'data': [
        'views/hr_leave_type.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
