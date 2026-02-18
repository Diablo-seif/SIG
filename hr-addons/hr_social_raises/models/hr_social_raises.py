""" HR Social Raises """

from odoo import api, fields, models


class HrSocialRaises(models.Model):
    """ HR Social Raises """
    _name = 'hr.social.raises'
    _description = 'Social Raises'
    _order = 'name'
    _sql_constraints = [
        ('unique_name', 'UNIQUE(name,employee_id)', 'Name must be unique'),
    ]

    name = fields.Char(
        'Year',
        required=True
    )
    percentage = fields.Float()
    min_salary = fields.Monetary()
    max_salary = fields.Monetary()
    insured_salary = fields.Monetary()
    raise_amount = fields.Monetary(
        compute='_compute_raise_amount'
    )
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id.id
    )
    employee_id = fields.Many2one(
        'hr.employee'
    )

    @api.depends('percentage', 'insured_salary', 'min_salary', 'max_salary')
    def _compute_raise_amount(self):
        """ Compute raise_amount value """
        for rec in self:
            raise_amount = rec.insured_salary * (rec.percentage / 100)
            if rec.min_salary:
                raise_amount = max(rec.min_salary, raise_amount)
            if rec.max_salary:
                raise_amount = min(rec.max_salary, raise_amount)
            rec.raise_amount = raise_amount
