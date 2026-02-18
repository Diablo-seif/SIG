""" inherit res.config.settings to add accounts of Deferred taxes"""

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    """
    inherit res.config.settings to add accounts of Deferred taxes
    """
    _inherit = 'res.config.settings'

    deferred_tax_liabilities_account_id = fields.Many2one(
        "account.account",
        related='company_id.deferred_tax_liabilities_account_id',
        readonly=False,
    )
    deferred_tax_assets_account_id = fields.Many2one(
        "account.account",
        related='company_id.deferred_tax_assets_account_id',
        readonly=False,
    )
    deferred_taxes_account_id = fields.Many2one(
        "account.account",
        related='company_id.deferred_taxes_account_id',
        readonly=False,
    )
