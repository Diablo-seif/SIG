""" Initialize Res Settings """

from odoo import fields, models


class ResCompany(models.Model):
    """
        Inherit Res Company:
         -
    """
    _inherit = 'res.company'

    overtime_type = fields.Selection(
        [('base_on_salary', 'Base On Salary'),
         ('base_on_leave', 'Base On Leave')],
        default='base_on_salary'
    )
    compensatory_percent = fields.Float()
    overtime_leave_type_id = fields.Many2one(
        'hr.leave.type'
    )
