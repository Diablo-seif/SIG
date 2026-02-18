# pylint: skip-file
{
    'name': 'Print Journal Entries',
    'summary': 'Print Journal Entries',
    'author': "CORE B.P.O",
    'maintainer': "Muhamed Abd El-Rhman, Abdalla Mohamed",
    'website': "http://www.core-bpo.com",
    # 'version': '1.0.0',
    'category': 'Accounting/Accounting',
    'license': 'OPL-1',
    'depends': [
        'account',
    ],
    'data': [
        'report/journal_entry_template.xml',
        'report/report.xml',
        'views/res_config_settings.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
