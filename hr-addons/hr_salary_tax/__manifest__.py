# pylint: skip-file
{
    'name': 'HR Salary Tax',
    'summary': 'HR Salary Tax',
    'author': "Muhamed Abd El-Rhman, CORE B.P.O",
    'website': "http://www.core-bpo.com",
    # 'version': '1.0.0',
    'category': 'Human Resources',
    'license': 'AGPL-3',
    'depends': [
        'hr_period',
        'l10n_eg_payroll',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_salary_tax.xml',
        'views/res_config_settings.xml',
        'views/hr_payslip.xml',
        'data/hr_salary_rule_category.xml',
        # 'data/hr_salary_rule.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
