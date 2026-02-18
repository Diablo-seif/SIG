"""inherit res.company to add accounts of Deferred taxes"""

from odoo import fields, models


class ResCompany(models.Model):
    """
    inherit res.company to add accounts of Deferred taxes
    """
    _inherit = 'res.company'

    deferred_tax_liabilities_account_id = fields.Many2one(
        "account.account",
    )
    deferred_tax_assets_account_id = fields.Many2one(
        "account.account",
    )
    deferred_taxes_account_id = fields.Many2one(
        "account.account",
    )
