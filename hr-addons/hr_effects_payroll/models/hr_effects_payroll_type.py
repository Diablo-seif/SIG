""" init object hr.effects.payroll.type """

from odoo import fields, models


class HrEffectsPayrollType(models.Model):
    """ init object hr.effects.payroll.type """
    _name = 'hr.effects.payroll.type'
    _description = "Hr Payroll Effects Type"

    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'The code must be unique !'),
    ]

    name = fields.Char(required=True, translate=True)
    effects_category = fields.Selection(
        [('additions', 'Additions'),
         ('deductions', 'Deductions')])
    code = fields.Char(required=True)
    active = fields.Boolean(default=True)
