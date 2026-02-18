""" HR Leave Allocation """
from datetime import datetime, time, timedelta
import pytz

from odoo import _, api, fields, models
from odoo.exceptions import UserError


# pylint: disable=no-member,protected-access,missing-return,invalid-name
# pylint: disable=cell-var-from-loop,too-many-nested-blocks
class HrLeaveAllocation(models.Model):
    """ inherit HR Leave Allocation """
    _inherit = 'hr.leave.allocation'

    calculation_method = fields.Selection(
        [('manual', 'Manual'), ('automatic', 'Automatic')], default='manual'
    )
    number_per_interval = fields.Float(digits=(2, 6))
    allocation_tag_id = fields.Many2one('hr.allocation.tag')
    contract_id = fields.Many2one('hr.contract')
    interval_unit = fields.Selection(
        selection=[('days', 'Days'), ('weeks', 'Weeks'),
                   ('months', 'Months'), ('years', 'Years')]
    )

    @api.model
    def _calculate_number_per_interval(self, allocation, employee):
        """ Calculate Number Per Interval """
        timezone = self.with_context(
            tz=self._context.get('tz') or self.env.user.partner_id.tz or 'UTC'
        )
        date_from = fields.Datetime.context_timestamp(
            timezone, (allocation.date_from + timedelta(days=1))
        )
        date_to = fields.Datetime.context_timestamp(
            timezone, (allocation.date_to + timedelta(days=-1))
        )
        calendar = self.resource_calendar_id or employee.resource_calendar_id
        calendar_days = len(calendar._get_day_total(date_from, date_to, None))
        interval_unit = {
            'days': calendar_days, 'weeks': 52, 'months': 12, 'years': 1
        }
        tag_line = allocation.holiday_status_id.tag_ids.filtered(
            lambda r: r.allocation_tag_id == employee.allocation_tag_id)
        if not tag_line:
            raise UserError(_('Please check allocation tag'))
        tag_days = tag_line.number_of_days
        allocation.interval_number = 1 if allocation.interval_unit == 'days' \
            else allocation.interval_number
        interval = interval_unit[allocation.interval_unit] / \
            allocation.interval_number
        allocation.number_per_interval = tag_days / interval
        allocation.unit_per_interval = 'days'
        allocation.calculation_method = 'automatic'

    def action_approve(self):
        """
        Calculate Number Per Interval automatically
        on approve if holiday type is employee
        """
        for allocation in self:
            if allocation.holiday_type == 'employee' and \
                    allocation.calculation_method == 'automatic' and \
                    allocation.allocation_type == 'accrual':
                allocation._calculate_number_per_interval(
                    allocation, allocation.employee_id)
        super().action_approve()

    def _prepare_holiday_values(self, employee):
        """ Prepare child allocation values """
        self.ensure_one()
        str_tz = self._context.get('tz') or self.env.user.partner_id.tz or 'UTC'
        tz = pytz.timezone(str_tz)
        date_from = self.date_from
        date_to = self.date_to
        contract = employee.contract_id
        if contract.date_start and contract.date_start > self.date_from.date():
            date_from = datetime.combine(contract.date_start, time(00, 00, 00))
            date_from = tz.localize(date_from, is_dst=False)
            date_from = date_from.astimezone(pytz.utc).replace(tzinfo=None)
        if contract.date_end and contract.date_end < self.date_to.date():
            date_to = datetime.combine(contract.date_end, time(23, 59, 59))
            date_to = tz.localize(date_to, is_dst=False)
            date_to = date_to.astimezone(pytz.utc).replace(tzinfo=None)
        if self.calculation_method == 'automatic':
            tag_line = self.holiday_status_id.tag_ids.filtered(
                lambda r: r.allocation_tag_id == employee.allocation_tag_id)
            if not tag_line:
                return False
            self._calculate_number_per_interval(self, employee)
        values = {
            'name': self.name,
            'holiday_type': 'employee',
            'holiday_status_id': self.holiday_status_id.id,
            'notes': self.notes,
            'number_of_days': self.number_of_days,
            'parent_id': self.id,
            'employee_id': employee.id,
            'allocation_type': self.allocation_type,
            'date_from': date_from,
            'date_to': date_to,
            'interval_unit': self.interval_unit,
            'interval_number': self.interval_number,
            'number_per_interval': self.number_per_interval,
            'unit_per_interval': self.unit_per_interval,
            'resource_calendar_id': self.resource_calendar_id.id,
            'limit_accrued_days': self.limit_accrued_days,
            'max_accrued_days': self.max_accrued_days,
            'limit_carryover_days': self.limit_carryover_days,
            'max_carryover_days': self.max_carryover_days,
            'limit_accumulated_days': self.limit_accumulated_days,
            'max_accumulated_days': self.max_accumulated_days,
            'accrual_method': self.accrual_method,
            'contract_id': employee.contract_id.id,
            'allocation_tag_id': employee.allocation_tag_id.id,
        }
        return values

    def _update_accrual(self):
        """
        Inherited to create new allocation for new employee and
        employee that gained new tag
        """
        today = fields.Date.from_string(fields.Date.today())
        allocations = self.search([
            ('allocation_type', '=', 'accrual'),
            ('parent_id', '=', False),
            ('state', '=', 'validate'),
            ('holiday_type', '!=', 'employee'),
            '|',
            ('date_to', '=', False), ('date_to', '>', fields.Datetime.now()),
            '|',
            ('nextcall', '=', False), ('nextcall', '<=', today)])
        for allocation in allocations:
            allocation._action_validate_create_childs()
        super()._update_accrual()

    @api.model
    def _create_child_allocation(self, allocation, employee):
        """
        - Create allocation for exist employees
        - Automatically create  Allocation for employee
          gained new tag or new contract
        """
        childs = self.env['hr.leave.allocation']
        holidays_values = allocation._prepare_holiday_values(employee)
        str_tz = self._context.get('tz') or self.env.user.partner_id.tz or 'UTC'
        tz = pytz.timezone(str_tz)
        if holidays_values:
            # check if employee already have child allocation
            # to prevent duplication when create allocation
            # for new employees or employees that gained new tag
            child_allocations = allocation.linked_request_ids.mapped(
                lambda r: (r.employee_id,
                           r.allocation_tag_id,
                           r.contract_id)
            )
            if (employee, employee.allocation_tag_id,
                    employee.contract_id) not in child_allocations:
                # End the old allocation for employees that gained
                # new tag and create new allocation with the new one
                for pair in child_allocations:
                    if employee == pair[0]:
                        date = datetime.combine(
                            fields.Date.today(), time(00, 00, 00))
                        date = tz.localize(date, is_dst=False)
                        date = date.astimezone(
                            pytz.utc).replace(tzinfo=None)
                        old_alc = allocation.linked_request_ids.filtered(
                            lambda r: r.employee_id == employee and
                            r.date_to > date
                        )
                        old_alc.date_to = date
                        holidays_values.update(date_from=date)
                childs += allocation.with_context(
                    mail_notify_force_send=False,
                    mail_activity_automation_skip=True
                ).create(holidays_values)
        return childs

    def _action_validate_create_childs(self):
        """ Create and validate allocation childs """
        childs = self.env['hr.leave.allocation']
        if self.state == 'validate' and \
                self.holiday_type in ['category', 'department', 'company']:
            if self.holiday_type == 'category':
                employees = self.category_id.employee_ids
            elif self.holiday_type == 'department':
                employees = self.department_id.member_ids
            else:
                employees = self.env['hr.employee'].search(
                    [('company_id', '=', self.mode_company_id.id)]
                )
            # Filter only employees that already have running contract
            employees = employees.filtered(
                lambda r: r.contract_id and r.contract_id.state == 'open')
            for employee in employees:
                childs += self._create_child_allocation(
                    allocation=self, employee=employee)
            childs.action_approve()
        return childs
