""" init object sale.order """

from odoo import models


class SaleOrder(models.Model):
    """ init object sale.order """
    _inherit = 'sale.order'

    # pylint: disable=no-member, protected-access, unused-argument
    def _create_invoices(self, grouped=False, final=False):
        """
        Override Super Create Invoice
        """
        moves = super(SaleOrder, self)._create_invoices()
        for move in moves:
            for line in move.invoice_line_ids:
                line.deduction_tax_id = line._get_deduction_tax()
        return moves
