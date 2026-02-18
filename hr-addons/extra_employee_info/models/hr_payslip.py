
from odoo import fields, models


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    employee_type = fields.Selection(related='employee_id.type', store=True)
    state_id = fields.Many2one(related='employee_id.state_id', store=True)