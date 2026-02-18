""" Inherit hr.department """

from odoo import fields, models

class HrDepartment(models.Model):
    """
        inherit hr.department:
    """
    _inherit = 'hr.department'

    budget_lines_ids = fields.One2many('department.budget.line', 'department_id')
    # payslip_ids = fields.One2many('hr.payslip', 'department_id')
    