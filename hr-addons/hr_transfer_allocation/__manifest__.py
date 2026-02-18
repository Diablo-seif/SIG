# pylint: disable=missing-docstring,manifest-required-author
{
    'name': 'HR Transfer Allocation',
    'summary': 'HR Transfer Allocation',
    'author': "Yousef Soliman, CORE B.P.O",
    'website': "http://www.core-bpo.com",
    # 'version': '13.0.1.0.0',
    'category': 'Human Resources',
    'license': 'AGPL-3',
    'depends': [
        'hr',
        'hr_holidays',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/hr_transfer_allocation_view.xml',
        'views/hr_transfer_allocation_view.xml',
        'data/ir_cron.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
