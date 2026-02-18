# pylint: disable=missing-docstring,manifest-required-author
{
    'name': 'Insurance Enroll Form',
    'summary': 'Insurance Enroll Form',
    'author': "Muhamed Abd El-Rhman, CORE B.P.O",
    'website': "http://www.core-bpo.com",
    # 'version': '1.0.0',
    'category': 'Human Resources',
    'license': 'AGPL-3',
    'depends': [
        'hr_employee_insurance',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/create_enroll_form.xml',
        'views/enroll_form.xml',
        'reports/paperformat.xml',
        'reports/reports.xml',
        'reports/report_layout.xml',
        'reports/enroll_form_template.xml',
        'data/ir_sequence.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
