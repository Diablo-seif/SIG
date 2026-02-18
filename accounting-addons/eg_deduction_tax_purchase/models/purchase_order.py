""" init object purchase.order """

from odoo import api, models


class AccountMove(models.Model):
    """ init object account.move """
    _inherit = 'account.move'

    @api.model
    # pylint: disable=protected-access
    def create(self, vals_list):
        """ Override create to set deduction tax """
        res = super(AccountMove, self).create(vals_list)
        for rec in res:
            for line in rec.invoice_line_ids:
                line.deduction_tax_id = line._get_deduction_tax()
        return res
