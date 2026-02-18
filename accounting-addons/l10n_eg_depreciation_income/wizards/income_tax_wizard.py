"""init income tax calculation wizard"""

from odoo import api, fields, models


class IncomeTaxWizard(models.TransientModel):
    """
    income tax wizard calculation
    """
    _inherit = "income.tax.wizard"
    # pylint: disable=protected-access
    depreciation_accounts = fields.Many2many(
        default=lambda self: self._get_default_depreciation_accounts()
    )
    tax_depreciation = fields.Monetary(readonly=True)

    @api.model
    def _get_default_depreciation_accounts(self):
        """
        get default depreciation accounts
        """
        categories = self.env['tax.depreciation.category'].search([])
        return categories.mapped('account_depreciation_ids')

    # pylint: disable=no-member
    def _calculate_tax_depreciation(self):
        """
        helper method to set tax_depreciation amount
        """
        computations = self.env[
            'tax.depreciation.category.asset.computation'
        ].search([('year', '=', self.year)])
        self.tax_depreciation = sum(
            computations.mapped('tax_depreciated_amount')
        )
