# pylint: disable=missing-docstring, manifest-required-author
{
    'name': "Holiday category in Time Off",
    'summary': "Define Holiday category in Time Off",
    'author': "Hashem Aly, CORE B.P.O",
    'website': "http://www.core-bpo.com",
    'category': 'hr',
    # 'version': '1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'hr_holidays',
    ],
    'data': [
        'views/hr_leave.xml',
        'views/hr_leave_allocation.xml',
        'views/hr_leave_type.xml',
    ],
}
