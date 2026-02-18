# pylint: skip-file
{
    'name': 'L10n Egypt Payroll',
    'summary': 'L10n Egypt Payroll',
    'author': "Muhamed Abd El-Rhman, CORE B.P.O",
    'website': "http://www.core-bpo.com",
    # 'version': '1.0.0',
    'category': 'Human Resources',
    'license': 'AGPL-3',
    'depends': [
        'hr_employee_insurance',
        'hr_work_entry_contract_enterprise',
    ],
    'data': [
        'data/hr_salary_rule_category.xml',
        'data/hr_payroll_structure.xml',
        'data/hr_salary_rule.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
