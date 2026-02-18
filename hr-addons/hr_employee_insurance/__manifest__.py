# pylint: disable=missing-docstring,manifest-required-author
{
    'name': 'HR Employee Insurance',
    'summary': 'HR Employee Insurance',
    'author': "Muhamed Abd El-Rhman, CORE B.P.O",
    'website': "http://www.core-bpo.com",
    # 'version': '1.0.0',
    'category': 'Human Resources',
    'license': 'AGPL-3',
    'depends': [
        'hr',
        'l10n_eg_social_insurance',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_employee.xml',
        'wizard/hr_departure_wizard.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'hr_employee_insurance/static/src/js/list_render.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
