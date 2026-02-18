""" Initialize Hr Loan Line as Installment """

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import date_utils


class HrLoanLine(models.Model):
    """ Initialize Hr Loan Line as Installment """
    _name = 'hr.loan.line'
    _description = 'Loan Installment'

    date = fields.Date(string='Payment Date', required=True)
    employee_id = fields.Many2one(related='loan_id.employee_id', store=True)
    amount = fields.Float(required=True)
    paid = fields.Boolean()
    loan_id = fields.Many2one('hr.loan', string='Loan Ref.')
    payslip_id = fields.Many2one('hr.payslip', string='Payslip Ref.')

    def unlink(self):
        """ Override unlink() to restrict delete if there is paid line """
        for line in self:
            if line.paid:
                raise UserError(_('You can\'t delete paid installment line'))
        return super().unlink()

    @api.constrains('date')
    def _check_date(self):
        """ Validate installments dates """
        for line in self:
            if line.date < line.loan_id.payment_date:
                raise UserError(_('You can\'t add installment with date '
                                  'before payment date'))
            date_from, date_to = date_utils.get_month(line.date)

            lines_count = self.sudo().search_count([
                ('loan_id', '=', line.loan_id.id),
                ('date', '>=', date_from),
                ('date', '<=', date_to)
            ])
            if lines_count > 1:
                raise UserError(_('You can\'t add 2 installments'
                                  ' in the same month'))
