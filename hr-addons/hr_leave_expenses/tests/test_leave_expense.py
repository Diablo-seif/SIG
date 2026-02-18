"""Tests for LeaveExpense"""

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
# pylint: disable=too-many-instance-attributes
class TestLeaveExpense(TransactionCase):
    """Integrated Tests"""

    def setUp(self):
        """Setup the testing environment."""
        super(TestLeaveExpense, self).setUp()
        self.employee1 = self.env["hr.employee"].create({
            'name': "test 1",
            'department_id': self.env.ref("hr.dep_rd").id
        })
        self.leave_type = self.env["hr.leave.type"].create({
            'name': "test type",
            'link_to_expenses': True,
            'leave_expense_ids': [
                (0, 0, {
                    'product_id': self.env.ref("product.expense_hotel").id,
                    'unit_amount': 100,
                    'department_ids': (4, self.employee1.department_id.id),
                }),
            ],
        })
        self.mission = self.env["hr.leave"].create({
            'name': "test type",
            'employee_id': self.employee1.id,
            'holiday_status_id': self.leave_type.id,
            'number_of_days': '1',
        })

    def test_01_leave_expense(self):
        """
        Test Scenario: create leave to employee
        and connect expense by department
        """
        self.mission.action_approve()
        self.assertTrue(self.mission.sheet_id)

    def test_02_leave_expense(self):
        """
        Test Scenario: create leave to employee
        and connect expense by department
        in case of double validation
        """
        self.leave_type.leave_validation_type = 'both'
        self.mission.action_validate()
        self.assertTrue(self.mission.sheet_id)
