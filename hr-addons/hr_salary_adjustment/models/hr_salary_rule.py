""" Hr Salary Rule """

from odoo import fields, models


class HrSalaryRule(models.Model):
    """ inherit Hr Salary Rule """
    _inherit = 'hr.salary.rule'

    appears_on_salary_adjustment = fields.Boolean()
    highlight_on_salary_adjustment = fields.Boolean()
    sequence_on_salary_adjustment = fields.Integer()
