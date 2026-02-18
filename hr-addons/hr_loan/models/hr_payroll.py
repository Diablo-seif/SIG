""" Inherit Hr payslip to integrate with loan """

from odoo import api, models


# pylint: disable=no-member,attribute-defined-outside-init
# pylint: disable=access-member-before-definition
class HrPayslip(models.Model):
    """
        Inherit Hr payslip:
         - integrate with loan
    """
    _inherit = 'hr.payslip'

    @api.onchange('employee_id', 'date_from', 'date_to')
    def onchange_employee_loan(self):
        """ onchange_employee """
        # Get exist payslip loan input lines to remove
        loan_inputs = self.input_line_ids.filtered(lambda r: r.loan_line_id)
        input_lines = [(3, loan.id) for loan in loan_inputs]
        # Get not paid loan installments and add input line for it
        loan_line_ids = self.env['hr.loan.line'].search([
            ('employee_id', '=', self.employee_id.id),
            ('loan_id.state', '=', 'approve'),
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('paid', '=', False)
        ])
        input_lines.extend([(0, 0, {
            'amount': line.amount,
            'loan_line_id': line.id,
            'input_type_id': self.env.ref(
                'hr_loan.hr_rule_loan_input_type').id
        }) for line in loan_line_ids])
        self.input_line_ids = input_lines

    def compute_sheet(self):
        """
            Override compute_sheet:
             - add loan input for employee if loan exist
        """
        for payslip in self:
            payslip.onchange_employee_loan()
        return super().compute_sheet()

    def action_payslip_done(self):
        """ Set loan installment paid on payslip done """
        self.input_line_ids.mapped('loan_line_id').write({'paid': True})
        return super().action_payslip_done()
