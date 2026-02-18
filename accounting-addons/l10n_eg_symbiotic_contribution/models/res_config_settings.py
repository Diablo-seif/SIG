""" inherit res.config.settings to add Deferred Tax Percentage"""

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    """
    inherit res.config.settings to add Deferred Tax Percentage
    and add accounts of Deferred taxes
    """
    _inherit = 'res.config.settings'

    symbiotic_contribution_percentage = fields.Float(
        related='company_id.symbiotic_contribution_percentage',
        readonly=False,
    )
    symbiotic_account_ids = fields.Many2many(
        related='company_id.symbiotic_account_ids',
        readonly=False,
    )
    symbiotic_entry_from_account_id = fields.Many2one(
        "account.account",
        related='company_id.symbiotic_entry_from_account_id',
        readonly=False,
    )
    symbiotic_entry_to_account_id = fields.Many2one(
        "account.account",
        related='company_id.symbiotic_entry_to_account_id',
        readonly=False,
    )
