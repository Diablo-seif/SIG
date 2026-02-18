
from odoo import fields, models


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    employee_type = fields.Selection(related='employee_id.type', store=True)
    state_id = fields.Many2one(related='employee_id.state_id', store=True)
    # department_id = fields.Many2one(related='employee_id.department_id', store=True)
    