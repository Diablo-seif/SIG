
from odoo import fields, models


class HrPayrollDeduction(models.Model):
    _name = 'hr.payroll.deduction'
    _description = 'hr.payroll.deduction'
    _rec_name = 'employee_id'
    
    employee_id = fields.Many2one('hr.employee', required=True)
    employee_type = fields.Selection(related='employee_id.type', store=True)
    state_id = fields.Many2one(related='employee_id.state_id', store=True)
    department_id = fields.Many2one(related='employee_id.department_id', store=True)
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    deduction_leave_days = fields.Float()
    management_penalty_days = fields.Float()
    tardiness_days = fields.Float()
    unattended_days = fields.Float()
    absence_penalty_days = fields.Float()
    

