""" Initialize Hr Salary Tax Apply Level """

from odoo import fields, models


class HrSalaryTaxApplyLevel(models.Model):
    """
        Initialize Hr Salary Tax Apply Level:
    """
    _name = 'hr.salary.tax.apply.level'
    _description = 'HR Salary Tax Apply Level'
    _order = 'level'
    _sql_constraints = [
        ('check_salary',
         'CHECK(salary_from <= salary_to)',
         'Salary from must be anterior to the salary to.'),
    ]

    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id.id
    )
    level = fields.Integer()
    salary_to = fields.Monetary(
        help='included in calculation',
    )
    salary_from = fields.Monetary(
        help='excluded in calculation',
    )
    salary_tax_id = fields.Many2one(
        'hr.salary.tax',
        ondelete='cascade'
    )
