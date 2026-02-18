# pylint: disable=missing-docstring, manifest-required-author
{
    'name': 'Contact Address',
    'summary': 'Base module for Contact Address',
    'author': 'CORE B.P.O',
    'website': 'http://www.core-bpo.com',
    'category': 'Hidden',
    # 'version': '1.0.0',
    'license': 'OPL-1',
    'depends': [
        'base',
        'contacts',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/res_zone.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
