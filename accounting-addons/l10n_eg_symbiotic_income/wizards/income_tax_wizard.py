"""init income tax calculation wizard"""

from odoo import models, fields


class IncomeTaxWizard(models.TransientModel):
    """
    income tax wizard calculation
    """
    _inherit = "income.tax.wizard"
    symbiotic_balance = fields.Monetary(readonly=True)

    # pylint: disable=no-member
    def _calculate_net_profit(self):
        """
        inherit method to auto calculate symbiotic_balance
        """
        symbiotic_acc = self.company_id.symbiotic_entry_from_account_id
        self.symbiotic_balance = self._get_accounts_balance(symbiotic_acc)
        return super(IncomeTaxWizard, self)._calculate_net_profit()
