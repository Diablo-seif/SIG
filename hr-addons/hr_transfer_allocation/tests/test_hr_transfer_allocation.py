"""Integrated Tests for hr employee"""

from odoo import fields

from odoo.tests.common import TransactionCase


# pylint: disable=too-many-instance-attributes
class TestHrTransferAllocation(TransactionCase):
    """ Unit test for object hr transfer allocation"""

    def setUp(self):
        """ Setup testing environment """
        super(TestHrTransferAllocation, self).setUp()
        self.hr_user = self.env.ref("base.user_demo")
        self.admin = self.env.ref("base.user_admin")
        self.leave_type = self.env.ref("hr_holidays.holiday_status_cl")
        self.employee = self.env['hr.employee'].create({
            'name': "Test Employee"
        })
        self.to_leave_type = self.env['hr.leave.type'].create({
            'name': "test Past",
            'responsible_id': self.admin.id,
            'allocation_type': 'fixed',
        })
        # @formatter:off
        self.scheduled_action_reset = self.env[
            'hr.transfer.allocation'].sudo().create({
                'name': "Test",
                "leave_ids": [(4, self.leave_type.id)],
                "employee_ids": [(4, self.employee.id)],
                "start_date": fields.Date.today(),
            })
        # @formatter:off
        self.scheduled_action_transfer = self.env[
            'hr.transfer.allocation'].sudo().create({
                'name': "Test",
                'method': "transfer",
                "leave_ids": [(4, self.leave_type.id)],
                "employee_ids": [(4, self.employee.id)],
                "start_date": fields.Date.today(),
                "to_leave_type_id": self.to_leave_type.id,
                "max_leaves": 4,
            })
        self.allocation = self.env['hr.leave.allocation'].create({
            'name': 'allocation',
            'employee_id': self.employee.id,
            'holiday_status_id': self.leave_type.id,
            'state': 'validate',
            'interval_number': 1,
            'number_per_interval': 1,
        })
        self.allocation_accural = self.env['hr.leave.allocation'].create({
            'name': 'allocation accural',
            'employee_id': self.employee.id,
            'holiday_status_id': self.leave_type.id,
            'state': 'validate',
            'allocation_type': 'accrual',
            'interval_number': 1,
            'number_per_interval': 1,
        })

    def test_close_on_schedule(self):
        """Run valid return """
        action = self.scheduled_action_reset.schedule_action()
        self.assertEqual(action['type'], 'ir.actions.act_window_close')

    def test_reset_transfer_cron(self):
        """Run Scheduled Reset/Transfer for valid scheduled"""
        scheduled_actions = self.env['hr.transfer.allocation'].search([
            ('state', '=', 'scheduled'),
            ('start_date', '<=', fields.Date.today())])
        self.env['hr.transfer.allocation'].sudo().reset_transfer_cron()
        for action in scheduled_actions:
            self.assertEqual(action.state, 'done')
        allocations_res = self.env['hr.leave.allocation'].search([
            ('employee_id', '=', self.employee.id),
            ('holiday_status_id.active', '=', True),
            ('holiday_status_id', '=', self.leave_type.id),
            ('holiday_status_id.allocation_type',
             'in', ['fixed', 'fixed_allocation']),
            ('state', '=', 'validate'),
            '|',
            ('date_to', '=', False),
            ('date_to', '>=', fields.Date.today()),
        ])
        allocations = self.env['hr.transfer.allocation'].sudo().get_allocations(
            self.leave_type.id, self.employee.id
        )
        self.assertEqual(allocations, allocations_res)
        self.assertEqual(
            self.allocation_accural.date_to.strftime('%Y-%m-%d'),
            fields.Date.today().strftime('%Y-%m-%d')
        )
        self.env['hr.leave.allocation'].create({
            'name': 'new ',
            'employee_id': self.employee.id,
            'holiday_status_id': self.leave_type.id,
            'state': 'validate',
            'number_of_days': 6,
            'interval_number': 1,
            'number_per_interval': 1,
        })

        allocation_new = self.scheduled_action_transfer.sudo().transfer()
        self.assertEqual(allocation_new.number_of_days, 4)
        # @formatter:off
        scheduled_action = self.env[
            'hr.transfer.allocation'].sudo().create({
                'name': "Test",
                'method': "transfer",
                "leave_ids": [(4, self.leave_type.id)],
                "employee_ids": [(4, self.employee.id)],
                "start_date": fields.Date.today(),
                "to_leave_type_id": self.to_leave_type.id,
            })
        self.env['hr.leave.allocation'].create({
            'name': 'allocation accural',
            'employee_id': self.employee.id,
            'holiday_status_id': self.leave_type.id,
            'state': 'validate',
            'interval_number': 1,
            'number_per_interval': 1,
        })
        allocation_new = scheduled_action.transfer()
        self.assertEqual(allocation_new.number_of_days, -15)
