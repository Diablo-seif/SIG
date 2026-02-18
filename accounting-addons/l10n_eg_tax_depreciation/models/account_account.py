"""inherit account account"""
from odoo import fields, models


class AccountAccount(models.Model):
    """ inherit account to add reverse to tax category """
    _inherit = 'account.account'

    tax_depreciation_category_fixed_id = fields.Many2one(
        'tax.depreciation.category',
    )
    tax_depreciation_category_depreciation_id = fields.Many2one(
        'tax.depreciation.category',
    )
