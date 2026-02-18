# pylint: skip-file
{
    'name': "Hr Calendar Time Off",
    'summary': "Integration between Calendar and Time Off",
    'author': "CORE B.P.O",
    'maintainer': 'Hashem Aly',
    'website': "http://www.core-bpo.com",
    'support': 'apps@core-bpo.com',
    'category': 'Human Resources',
    # 'version': '1.0.0',
    'license': 'OPL-1',
    'depends': [
        'calendar',
        'hr_holidays',
    ],
    'data': [
        'views/calendar_event.xml',
        'views/res_config_settings.xml',
    ],
    'images': [
        'static/description/banner.gif',
        'static/description/main_screenshot.gif',
        'static/description/corebpo_logo.png',
        'static/description/configuration.png',
        'static/description/invitation_mail.png',
        'static/description/schedule_meeting.png',
        'static/description/timeoff_requests.png',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'price': 15,
    'currency': 'USD',
}
