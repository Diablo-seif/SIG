{
    'name': "Hr Contract Egypt Tax Calculation Net to Gross",
    'summary': "Calculate employee contract wage from net to gross",
    'author': "Abdalla Mohamed, CORE B.P.O",
    'website': "http://www.core-bpo.com",
    'category': 'Human Resourses',
    # 'version': '1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'hr_contract',
        'hr_salary_tax',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizards/hr_contract_wage_calculate.xml',
        'views/hr_contract.xml',
        'views/hr_employee.xml',
        'data/ir_action_server.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
# pylint: skip-file
