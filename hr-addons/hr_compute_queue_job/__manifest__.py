# pylint: disable=missing-docstring, manifest-required-author
{
    'name': "Compute Attendance With Queue JOB",
    'summary': "hr Compute Attendance With Queue JOB",
    'author': "Hashem Aly, CORE B.P.O",
    'website': "http://www.core-bpo.com",
    'category': 'hr',
    # 'version': '1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'hr_compute_attendance',
        'queue_job',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        # View Files
        'views/hr_compute_attendance.xml',
        'views/hr_compute_attendance_line.xml',
        # Wizard Files
        'wizard/hr_compute_wizard.xml',
        # Data Files
        'data/queue_job.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
