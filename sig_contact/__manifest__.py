# pylint: disable=skip-file
{
    'name': 'SIG Contacts',
    'summary': 'SIG Contacts',
    'author': "Mohamed Osama, CORE B.P.O",
    'website': "http://www.core-bpo.com",
    'sequence': 1,
    # 'version': '1.0.9',
    'depends': [
        'base',
        'account',
        'contacts',
        'purchase',
    ],
    'data': [
        # 'security/security.xml',
        'security/ir.model.access.csv',
        'views/res_partner.xml',
        'views/account_payment.xml',
        'views/purchase_rfq.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
