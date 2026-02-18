""" init object account.fiscal.position """

from odoo import models, api


# pylint: disable=no-member, unused-argument, too-many-boolean-expressions
class AccountFiscalPosition(models.Model):
    """ init object account.fiscal.position """
    _inherit = 'account.fiscal.position'

    @api.model
    def map_tax(self, taxes, product=None, partner=None, date=None):
        """
        Action mapping tax
        """
        def matched_line(tax, tax_line, date):
            """
            Check Matched Lines
            """
            res = False
            if tax_line.tax_src_id == tax:
                if not date:
                    if not tax_line.date_from \
                            and not tax_line.date_to:
                        res = True
                else:
                    if (
                            not tax_line.date_from and not tax_line.date_to
                    ) or (
                        tax_line.date_from and tax_line.date_to and
                        tax_line.date_from <= date <= tax_line.date_to
                    ) or (
                        tax_line.date_from and not tax_line.date_to and
                        date >= tax_line.date_from
                    ) or (
                        not tax_line.date_from and tax_line.date_to and
                        date <= tax_line.date_to
                    ):
                        res = True

            return res

        result = self.env['account.tax'].browse()
        for tax in taxes:
            tax_count = 0
            for tax_line in self.tax_ids:
                if matched_line(tax, tax_line, date):
                    tax_count += 1
                    if tax_line.tax_dest_id:
                        result |= tax_line.tax_dest_id
            if not tax_count:
                result |= tax
        return result
