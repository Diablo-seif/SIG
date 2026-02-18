# pylint: skip-file
{
    'name': 'Journal Entries Category Print',
    'summary': 'Journal Entries Category Print',
    'author': "Muhamed Abd El-Rhman, CORE B.P.O",
    'website': "http://www.core-bpo.com",
    # 'version': '0.1.0',
    'category': 'Accounting/Accounting',
    'license': 'AGPL-3',
    'depends': [
        'journal_entry_print',
        'journal_entry_category',
    ],
    'data': [
        'report/journal_entry_template.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
}
