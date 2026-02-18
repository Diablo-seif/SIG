# pylint: skip-file
{
    'name': 'Journal Entries Cost Center Print',
    'summary': 'Journal Entries Cost Center Print',
    'author': "Muhamed Abd El-Rhman, CORE B.P.O",
    'website': "http://www.core-bpo.com",
    # 'version': '13.0.0.1.0',
    'category': '',
    'license': 'AGPL-3',
    'depends': [
        'journal_entry_print',
        'account_cost_center',
    ],
    'data': [
        'report/journal_entry_template.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
}
