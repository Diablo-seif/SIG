# pylint: disable=missing-docstring, manifest-required-author
{
    'name': 'Apply Deduction Taxes On Purchases',
    'summary': 'Apply Deduction Taxes On Purchases',
    'author': "Hashem Aly, CORE B.P.O",
    'website': "http://www.core-bpo.com",
    'category': 'Operations/Purchase',
    # 'version': '0.1.0',
    'license': 'AGPL-3',
    'depends': [
        'purchase',
        'l10n_eg_deduction_tax',
    ],
    'data': [
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
