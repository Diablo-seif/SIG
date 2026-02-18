""" Inherit hr employee to link with loans. """
from odoo import fields, models


class HrEmployee(models.Model):
    """
        Inherit hr employee:
         - Link with loans
    """
    _inherit = 'hr.employee'

    loan_ids = fields.One2many(
        'hr.loan', 'employee_id', groups='hr.group_hr_user'
    )
    loan_count = fields.Integer(
        compute='_compute_employee_loans', groups='hr.group_hr_user'
    )
    loan_amount = fields.Monetary(
        currency_field='currency_id', compute='_compute_employee_loans',
        groups='hr.group_hr_user'
    )
    currency_id = fields.Many2one(
        'res.currency', default=lambda self: self.env.company.currency_id,
        groups='hr.group_hr_user'
    )

    def _compute_employee_loans(self):
        """
            compute the loan amount and total loans for the employee.
        """
        for employee in self:
            employee.loan_count = len(employee.loan_ids)
            employee.loan_amount = sum(employee.mapped('loan_ids.loan_amount'))

    def action_view_loans(self):
        """ :return action to view employee loans """
        loans = self.mapped('loan_ids')
        action = self.env.ref('hr_loan.hr_loan_action').read()[0]
        action['domain'] = [('id', 'in', loans.ids)]
        if len(loans) == 1:
            action['views'] = [(self.env.ref(
                'hr_loan.hr_loan_form').id, 'form')]
            action['res_id'] = loans.ids[0]
        return action
