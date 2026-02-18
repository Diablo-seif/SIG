"""inherit res.company to add Deferred Tax Percentage"""

from odoo import fields, models


class ResCompany(models.Model):
    """
    inherit res.company to add Deferred Tax Percentage
    and add accounts of Deferred taxes
    """
    _inherit = 'res.company'

    symbiotic_contribution_percentage = fields.Float()

    symbiotic_account_ids = fields.Many2many(
        "account.account",
        "symbiotic_contribution_accounts",
        "symbiotic_contribution_id",
        "account_id",
    )
    symbiotic_entry_from_account_id = fields.Many2one(
        "account.account",
    )
    symbiotic_entry_to_account_id = fields.Many2one(
        "account.account",
    )
