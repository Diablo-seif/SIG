""" Initialize Account Tax """

from odoo import fields, models


class AccountTax(models.Model):
    """
        Inherit Account Tax:
    """
    _inherit = 'account.tax'

    is_taxable = fields.Boolean(default=True)
    code = fields.Char()
