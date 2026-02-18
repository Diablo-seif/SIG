""" Initialize Hr Employee Overtime """

from odoo.addons.resource.models.resource import HOURS_PER_DAY

from odoo import api, fields, models


class HrEmployeeOvertime(models.Model):
    """
        Inherit Hr Employee Overtime:
         - 
    """
    _inherit = 'hr.employee.overtime'

    overtime_type = fields.Selection(
        [('base_on_salary', 'Base On Salary'),
         ('base_on_leave', 'Base On Leave')],
        readonly=True
    )
    overtime_leave_type_id = fields.Many2one(
        'hr.leave.type',
        readonly=True
    )

    @api.model
    def create(self, vals_list):
        """ Override create """
        if 'overtime_type' not in vals_list:
            vals_list.update({'overtime_type': self.env.company.overtime_type})
        if 'overtime_leave_type_id' not in vals_list:
            vals_list.update({
                'overtime_leave_type_id': self.env.company.overtime_leave_type_id.id
            })
        return super(HrEmployeeOvertime, self).create(vals_list)

    def emp_overtime_approve(self):
        """ Override emp_overtime_approve """
        res = super(HrEmployeeOvertime, self).emp_overtime_approve()
        compensatory_percent = self.env.company.compensatory_percent
        self.env['hr.leave.allocation'].with_context({
            'default_overtime': True,
            'default_overtime_number': self.overtime / 60 * compensatory_percent / 100,
        }).create({
            'name': f'{self.employee_id.name} Overtime',
            'holiday_type': 'employee',
            'employee_id': self.employee_id.id,
            'holiday_status_id': self.overtime_leave_type_id.id,
        })
        return res


class HrLeaveAllocation(models.Model):
    """
        Inherit Hr Leave Allocation:
         - 
    """
    _inherit = 'hr.leave.allocation'

    overtime = fields.Boolean()
    overtime_number = fields.Float()

    @api.depends('number_of_days', 'employee_id')
    def _compute_number_of_hours_display(self):
        for allocation in self:
            if not allocation.overtime:
                if allocation.parent_id and allocation.parent_id.type_request_unit == "hour":
                    allocation.number_of_hours_display = allocation.number_of_days * HOURS_PER_DAY
                elif allocation.number_of_days:
                    allocation.number_of_hours_display = allocation.number_of_days * (
                            allocation.employee_id.sudo().resource_id.calendar_id.hours_per_day or HOURS_PER_DAY)
                else:
                    allocation.number_of_hours_display = 0.0
            else:
                allocation.number_of_hours_display = allocation.overtime_number
