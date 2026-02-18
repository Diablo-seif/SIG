# pylint: skip-file
{
    'name': 'Time Off Limitations',
    'summary': 'Limit Employee request time off before contract start date',
    'author': "CORE B.P.O",
    'maintainer': 'Muhamed Abd El-Rhman',
    'website': "http://www.core-bpo.com",
    # 'version': '1.0.0',
    'category': 'Human Resources',
    'license': 'OPL-1',
    'depends': [
        'hr_holidays',
        'hr_contract',
    ],
    'data': [
        'views/hr_leave_type.xml',
        'views/hr_contract.xml',
    ],
    'images': [
        'static/description/banner.gif',
        'static/description/main_screenshot.gif',
        'static/description/corebpo_logo.png',
        'static/description/corebpo_logo_screenshot.png',
        'static/description/employee_contract.png',
        'static/description/timeoff_contract_limitation.png',
        'static/description/timeoff_no_of_days.png',
        'static/description/timeoff_no_of_hours.png',
        'static/description/timeoff_request_contract.png',
        'static/description/timeoff_request_days_before.png',
        'static/description/timeoff_request_hours_before.png',
    ],

    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 30,
    'currency': 'USD',
}
