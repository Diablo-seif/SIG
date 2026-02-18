""" HR Salary Tax Line """

from odoo import api, fields, models


class HrSalaryTaxLine(models.Model):
    """ HR Salary Tax Line """
    _name = 'hr.salary.tax.line'
    _description = 'HR Salary Tax Line'
    _order = 'level'
    _sql_constraints = [
        ('check_salary',
         'CHECK(salary_from <= salary_to)',
         'Salary from must be anterior to the salary to.'),
        ('check_level',
         'CHECK(level > 0)',
         'Level cannot be less than or equal to zero'),
        ('unique_level',
         'UNIQUE(level,salary_tax_id)',
         'Level must be unique'),
    ]

    level = fields.Integer()
    salary_from = fields.Monetary(
        help='excluded in calculation',
    )
    salary_to = fields.Monetary(
        help='included in calculation',
    )
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id.id
    )
    line_amount = fields.Float(
        compute='_compute_line_amount',
        store=True
    )
    additional_tax_percentage = fields.Float(
        compute='_compute_line_amount',
        store=True
    )
    tax_percentage = fields.Float()
    refund_percentage = fields.Float()
    salary_tax_id = fields.Many2one(
        'hr.salary.tax',
        ondelete='cascade'
    )

    @api.depends('salary_from', 'salary_to', 'tax_percentage')
    def _compute_line_amount(self):
        """ Compute line_amount value """
        for rec in self:
            line_amount = abs(rec.salary_to - rec.salary_from)
            rec.line_amount = line_amount
            rec.additional_tax_percentage = line_amount * rec.tax_percentage
