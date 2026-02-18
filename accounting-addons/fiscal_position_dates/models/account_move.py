""" init object account.move"""

from odoo import models, api


# pylint: disable=no-member, protected-access
class AccountMove(models.Model):
    """ init object account.move"""
    _inherit = 'account.move'

    @api.onchange('invoice_date')
    def _onchange_invoice_date(self):
        """
        Onchange invoice_date
        """
        res = super(AccountMove, self)._onchange_invoice_date()
        for line in self.invoice_line_ids:
            taxes = line._get_computed_taxes()
            if taxes and line.move_id.fiscal_position_id:
                taxes = line.move_id.fiscal_position_id.map_tax(
                    taxes,
                    partner=line.partner_id,
                    date=self.invoice_date
                )
            line.tax_ids = taxes
        return res
