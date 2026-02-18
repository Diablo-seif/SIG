# pylint: skip-file
{
    'name': 'Hr Expiry Dates',
    'summary': 'Add Expiry Dates in Employee (ID and Passport)',
    'author': 'CORE B.P.O',
    'maintainer': 'Hashem Aly',
    'website': 'http://www.core-bpo.com',
    'support': 'apps@core-bpo.com',
    'category': 'Human Resources',
    # 'version': '1.0.0',
    'license': 'OPL-1',
    'depends': [
        'hr',
    ],
    'data': [
        'views/hr_employee.xml',
    ],
    'images': [
        'static/description/banner.gif',
        'static/description/main_screenshot.gif',
        'static/description/corebpo_logo.png',
        'static/description/banner.png',
        'static/description/expirt_dates.png',
        'static/description/logo.png',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'price': 15,
    'currency': 'USD',
}
