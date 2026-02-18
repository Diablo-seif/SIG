""" Inherit account.move.line to integrate with loans """

from odoo import fields, models


# pylint: disable=protected-access, no-member
class AccountMoveLine(models.Model):
    """ Inherit account.move.line to integrate with loans """
    _inherit = "account.move.line"

    loan_id = fields.Many2one(
        'hr.loan', copy=False, help='Loan where the move line come from'
    )

    def reconcile(self):
        """
        Override Reconcile
        :return: res
        """
        not_paid_loans = self.loan_id.filtered(
            lambda expense: expense.payments_paid is False)
        res = super().reconcile()
        not_paid_loans.set_to_paid()
        return res
