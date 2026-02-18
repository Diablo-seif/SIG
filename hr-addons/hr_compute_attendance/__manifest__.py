# pylint: disable=missing-docstring, manifest-required-author
{
    'name': "Compute Attendance",
    'summary': "Compute Attendance To Create per day records",
    'author': "Hashem Aly, CORE B.P.O",
    'website': "http://www.core-bpo.com",
    'category': 'hr',
    # 'version': '1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'hr_attendance',
        'hr_contract',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        # View Files
        'views/hr_attendance_record.xml',
        'views/hr_compute_attendance.xml',
        'views/hr_compute_attendance_line.xml',
        'views/hr_plenty_rule.xml',
        'views/resource_calendar.xml',
        'views/resource_calendar_attendance.xml',
        'views/resource_calendar_flexible.xml',
        'views/res_config_settings.xml',
        # Data Files
        'data/hr_compute_attendance.xml',
        'data/ir_config_parameter.xml',
    ],
    'demo': [
        'demo/hr_plenty_rule.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
