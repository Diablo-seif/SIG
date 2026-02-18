""" Test HR Leave Allocation """
from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.tests.common import TransactionCase


# pylint: disable=no-member,protected-access,
class TestHrLeaveAllocation(TransactionCase):
    """ Test for test_hr_leave_allocation model """

    def setUp(self):
        """ Setup testing environment """
        super().setUp()
        date = fields.datetime.now()
        self.tag_21 = self.env.ref('hr_allocation_calculation.21_days')
        self.tag_30 = self.env.ref('hr_allocation_calculation.30_days')
        self.emp_21 = self.env.ref('hr.employee_al')
        self.emp_30 = self.env.ref('hr.employee_mit')
        self.emp_21.allocation_tag_id = self.tag_21
        self.emp_30.allocation_tag_id = self.tag_30
        self.allocation_comp = self.env['hr.leave.allocation'].create({
            'name': 'Test Accrual',
            'state': 'validate',
            'holiday_status_id': self.env.ref(
                'hr_allocation_calculation.holiday_status_annual').id,
            'allocation_type': 'accrual',
            'holiday_type': 'company',
            'mode_company_id': self.env.company.id,
            'date_from': date + relativedelta(
                month=1, day=1, hour=0, minute=0, second=0),
            'date_to': date + relativedelta(
                month=12, day=31, hour=23, minute=59, second=59),
            'calculation_method': 'automatic',
            'resource_calendar_id':
                self.env.ref('resource.resource_calendar_std').id,
            'employee_id': self.emp_21.id,
        })
        self.allocation_dep = self.env['hr.leave.allocation'].create({
            'name': 'Test Accrual',
            'state': 'validate',
            'holiday_status_id': self.env.ref(
                'hr_allocation_calculation.holiday_status_annual').id,
            'allocation_type': 'accrual',
            'holiday_type': 'department',
            'department_id': self.env.ref('hr.dep_ps').id,
            'date_from': date + relativedelta(
                month=1, day=1, hour=0, minute=0, second=0),
            'date_to': date + relativedelta(
                month=12, day=31, hour=23, minute=59, second=59),
            'calculation_method': 'automatic',
            'resource_calendar_id':
                self.env.ref('resource.resource_calendar_std').id,
            'employee_id': self.emp_21.id,
        })
        self.allocation_cat = self.env['hr.leave.allocation'].create({
            'name': 'Test Accrual',
            'state': 'validate',
            'holiday_status_id': self.env.ref(
                'hr_allocation_calculation.holiday_status_annual').id,
            'allocation_type': 'accrual',
            'holiday_type': 'category',
            'category_id': self.env.ref('hr.employee_category_2').id,
            'date_from': date + relativedelta(
                month=1, day=1, hour=0, minute=0, second=0),
            'date_to': date + relativedelta(
                month=12, day=31, hour=23, minute=59, second=59),
            'calculation_method': 'automatic',
            'resource_calendar_id':
                self.env.ref('resource.resource_calendar_std').id,
            'employee_id': self.emp_21.id,
        })

    def test_accrual(self):
        """ Test Scenario: test accrual() """
        self.allocation_comp._update_accrual()
        self.assertEqual(len(self.allocation_comp.linked_request_ids), 2)
        self.emp_21.allocation_tag_id = self.tag_30
        self.allocation_comp._update_accrual()
        self.assertEqual(len(self.allocation_comp.linked_request_ids), 3)
        self.allocation_dep._update_accrual()
        self.assertEqual(len(self.allocation_dep.linked_request_ids), 0)
        self.allocation_cat._update_accrual()
        self.assertEqual(len(self.allocation_cat.linked_request_ids), 0)
