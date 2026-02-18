""" inherit res.config.settings to add income tax entry accounts"""

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    """
    inherit res.config.settings to add income tax entry accounts
    """
    _inherit = 'res.config.settings'

    income_tax_entry_from_account_id = fields.Many2one(
        "account.account",
        related='company_id.income_tax_entry_from_account_id',
        readonly=False
    )
    income_tax_rounding = fields.Selection(
        related='company_id.income_tax_rounding', readonly=False)
    income_tax_rounding_base = fields.Integer(
        related='company_id.income_tax_rounding_base', readonly=False)
    base_after_losses_rounding = fields.Selection(
        related='company_id.base_after_losses_rounding', readonly=False)
    base_after_losses_rounding_base = fields.Integer(
        related='company_id.base_after_losses_rounding_base', readonly=False)
