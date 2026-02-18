""" Initialize Account Tax Group """

from odoo import fields, models


class AccountTaxGroup(models.Model):
    """
        Inherit Account Tax Group:
    """
    _inherit = 'account.tax.group'

    code = fields.Char()
