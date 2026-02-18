""" init hr.evaluation.period """
from odoo import fields, models


class HrPerformancePeriod(models.Model):
    """
    init hr.evaluation.period
    """
    _name = 'hr.evaluation.period'
    _description = 'HR evaluation Period'
    _sql_constraints = [
        ('check_dates',
         'CHECK(start_date <= end_date)',
         'Start date must be anterior to the end date.'),
    ]

    name = fields.Char(
        required=True,
    )
    start_date = fields.Date(
        required=True,
    )
    end_date = fields.Date(
        required=True,
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        default=lambda self: self.env.company,
    )
