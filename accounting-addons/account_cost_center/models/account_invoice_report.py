""" init object account.invoice.report  """

from odoo import fields, models


# pylint: disable=no-member
class AccountInvoiceReport(models.Model):
    """ init object account.invoice.report  """
    _inherit = 'account.invoice.report'

    cost_center_id = fields.Many2one(
        'account.cost.center', string='Cost Center', readonly=True)

    def _select(self):
        """
        Override Select Query
        """
        new_seleect = ", line.cost_center_id as cost_center_id"
        return super(AccountInvoiceReport, self)._select() + new_seleect

    def _group_by(self):
        """
        Override group_by Query
        """
        new_seleect = ", line.cost_center_id"
        return super(AccountInvoiceReport, self)._group_by() + new_seleect
