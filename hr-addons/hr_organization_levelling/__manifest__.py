# pylint: skip-file
{
    'name': 'HR Organization levelling',
    'summary': 'HR Organization levelling',
    'author': "Muhamed Abd El-Rhman, CORE B.P.O",
    'website': "http://www.core-bpo.com",
    # 'version': '1.0.0',
    'category': 'Human Resources',
    'license': 'AGPL-3',
    'depends': [
        'hr'
    ],
    'data': [
        'security/ir_rule.xml',
        'security/ir.model.access.csv',
        'views/hr_job_level.xml',
        'views/res_config_settings.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
