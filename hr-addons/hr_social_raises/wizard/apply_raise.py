""" Apply Raise """
from odoo import fields, models


class ApplyRaise(models.TransientModel):
    """ Apply Raise """
    _name = 'apply.raise'
    _description = 'Apply Raise'

    name = fields.Char(
        'Year',
        required=True
    )
    percentage = fields.Float()
    min_salary = fields.Monetary()
    max_salary = fields.Monetary()
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id.id
    )

    def apply_raise(self):
        """ Apply Raise """
        self.ensure_one()
        active_ids = self.env.context.get('active_ids')
        employees = self.env['hr.employee'].browse(active_ids).filtered(
            lambda r: r.insured and r.contract_id.state == 'open'
        )
        for employee in employees:
            employee.raises_ids = [(0, 0, {
                'name': self.name,
                'percentage': self.percentage,
                'min_salary': self.min_salary,
                'max_salary': self.max_salary,
                'insured_salary': employee.insured_salary,
            })]
