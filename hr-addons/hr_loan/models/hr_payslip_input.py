""" Initialize Hr Payslip Input to integrate with loan """
from odoo import fields, models


class HrPayslipInput(models.Model):
    """
        Inherit Hr payslip input:
         - integrate with loan
    """
    _inherit = 'hr.payslip.input'

    loan_line_id = fields.Many2one('hr.loan.line', string='Loan Installment')
