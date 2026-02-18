""" HR Transfer Allocation """
import datetime

from odoo import _, fields, models


# pylint: disable=no-self-use,inconsistent-return-statements
class HrTransferAllocation(models.Model):
    """ HR Transfer Allocation """
    _name = 'hr.transfer.allocation'
    _description = 'HR Transfer Allocation'

    name = fields.Char(string="Title", required=True)
    leave_ids = fields.Many2many(
        "hr.leave.type", string="From Leave Types", required=True
    )
    employee_ids = fields.Many2many(
        "hr.employee", string="Employees", required=True
    )
    method = fields.Selection(
        [
            ("reset", "Reset"),
            ("transfer", "Transfer")
        ], default="reset"
    )
    to_leave_type_id = fields.Many2one(
        "hr.leave.type",
        domain="[('allocation_type','in', ['fixed', 'fixed_allocation'])]",
    )
    max_leaves = fields.Float("Max", default=0.0)
    start_date = fields.Date(
        'Reset/Transfer Date', required=True, default=fields.Date.today()
    )
    state = fields.Selection(
        [
            ('scheduled', 'Scheduled'),
            ('done', 'Done'),
        ], default='scheduled'
    )

    _sql_constraints = [(
        'start_date_check',
        'CHECK ((CURRENT_DATE <= start_date))',
        _('The start date must be greater than today')
    ), (
        'negative_max',
        'CHECK ((max_leaves >= 0))',
        _('Max must be greater than Zero')
    )]

    def schedule_action(self):
        """Close on click button Schedule Transfer"""
        action = {'type': 'ir.actions.act_window_close'}
        return action

    def reset_transfer_cron(self):
        """Run Scheduled Reset/Transfer for valid scheduled"""
        scheduled_actions = self.search([
            ('state', '=', 'scheduled'),
            ('start_date', '<=', fields.Date.today())])

        for action in scheduled_actions:
            action.transfer()

    # pylint: disable=protected-access
    def reset_allocations(self, remaining_leaves, allocations):
        """
        Reset Allocations
        - Reset allocation(remaining_leaves) of selected types
        of selected employees to be 0
        :param:allocations(hr.leave.allocation)
        :param:remaining_leaves(int) total remaining leaves of employee
        """
        for allocation in allocations:
            if allocation.allocation_type == 'accrual':
                allocation.date_to = fields.Datetime.now()
            if remaining_leaves > 0:
                allocation._compute_from_holiday_status_id()
                val_list = {
                    'number_of_days': -1 * remaining_leaves,
                    'name': _('Reconciled Allocation'),
                    'state': 'validate',
                }
                allocation.copy(val_list)

    def transfer_to_leave(self, employee_id, total_leaves):
        """
        Transfer Allocations
        - Transfer allocation(remaining_leaves) of selected types
        of selected employee
        :param:employee_id(id:hr.employee) id of employee
        :param:total_leaves(int) total leaves of employee
        """
        if self.to_leave_type_id:
            if self.max_leaves:
                number_of_days = min(self.max_leaves, total_leaves)
            else:
                number_of_days = total_leaves
            vals = {
                'name': _('Transferred Allocation'),
                'holiday_status_id': self.to_leave_type_id.id,
                'state': 'validate',
                'employee_id': employee_id,
                'number_of_days': number_of_days,
            }
            allocation = self.env['hr.leave.allocation'].new(vals)
            allocation._compute_from_holiday_status_id()
            return self.env['hr.leave.allocation'].create(
                allocation._convert_to_write(allocation._cache))

    def get_leaves(self, leave_type_id, employee_id):
        """get valid leaves
        :param:leave_type_id(id:hr.leave.type) type of leave
        :param:employee_id(id:hr.employee) id of employee
        :return: hr.leave objects
        """
        leaves = self.env['hr.leave'].search([
            ('employee_id', '=', employee_id),
            ('holiday_status_id.active', '=', True),
            ('holiday_status_id', '=', leave_type_id),
            ('state', '=', 'validate'),
            ('holiday_status_id.allocation_type',
             'in', ['fixed', 'fixed_allocation']),
        ])
        return leaves

    def get_allocations(self, leave_type_id, employee_id):
        """get valid allocations

        :param:leave_type_id(id:hr.leave.type) type of leave
        :param:employee_id(id:hr.employee) id of employee
        :return: hr.leave.allocation objects
        """
        allocations = self.env['hr.leave.allocation'].search([
            ('employee_id', '=', employee_id),
            ('holiday_status_id.active', '=', True),
            ('holiday_status_id', '=', leave_type_id),
            ('holiday_status_id.allocation_type',
             'in', ['fixed', 'fixed_allocation']),
            ('state', '=', 'validate'),
            '|',
            ('date_to', '=', False),
            ('date_to', '>=', datetime.date.today()),
        ])
        return allocations

    def transfer(self):
        """
        Transfer/Reset Allocations
        - Reset allocation(remaining_leaves) of selected types
          of selected employees to be 0
        - Transfer allocation(remaining_leaves) of selected types
          of selected employees to selected type
        """
        self.ensure_one()
        self.state = "done"
        employee_ids = self.employee_ids
        for employee_id in employee_ids:
            total_leaves = 0
            for leave_id in self.leave_ids:
                leaves = self.get_leaves(leave_id.id, employee_id.id)
                allocations = self.get_allocations(leave_id.id, employee_id.id)
                # @formatter:off
                remaining_leaves = sum(allocations.mapped('number_of_days')) - \
                    sum(leaves.mapped('number_of_days'))
                total_leaves += remaining_leaves
                self.reset_allocations(remaining_leaves, allocations)
            if self.method == 'transfer':
                return self.transfer_to_leave(employee_id.id, total_leaves)
