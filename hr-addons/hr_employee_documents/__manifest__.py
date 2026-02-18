# pylint: disable=missing-docstring,manifest-required-author
{
    'name': 'HR Employee Document',
    'summary': 'HR Employee Document',
    'author': "Muhamed Abd El-Rhman, CORE B.P.O",
    'website': "http://www.core-bpo.com",
    # 'version': '13.0.1.0.0',
    'category': 'Human Resources',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'hr',
        # 'hr_employee_responsible'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_employee.xml',
        'views/hr_employee_documents.xml',
        'views/hr_employee_documents_lines.xml',
        'views/res_config_settings.xml',
        'data/hr_employee_documents.xml',
        'data/ir.cron.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
