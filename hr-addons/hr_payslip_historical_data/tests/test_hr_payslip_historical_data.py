"""Integrated Tests for Gift"""

from odoo.tests.common import TransactionCase


# pylint: disable=too-many-instance-attributes,protected-access
class TestHrHistoricalData(TransactionCase):
    """Integrated Tests"""

    def setUp(self):
        """ Setup testing environment """
        super(TestHrHistoricalData, self).setUp()
        self.historical_data_user = self.env['res.users'].create({
            'name': 'Sample User Manage Historical Data',
            'login': 'manage_historical_data',
            'email': 'manage_historical_data@example.com',
            'groups_id': [
                (6, 0, [self.env.ref('hr_payroll.group_hr_payroll_manager').id])
            ]
        })
        self.employee = self.env.ref('hr.employee_admin')

    def test_01_create_historical_data(self):
        """Test Scenario: Create Hr Payslip Historical Data."""
        historical_data = self.env['hr.payslip.historical.data'].with_user(
            self.historical_data_user).create({
                'employee_id': self.employee.id,
                'month': 1,
                'year': 2018,
                'value': 1000,
            })
        self.assertTrue(historical_data,
                        "test create hr payslip historical data done.")

    def test_02_payslip_confirm(self):
        """Test Scenario: When Payslip Confirm Create Historical Data."""
        payslip = self.env['hr.payslip'].create({
            'name': self.employee.name,
            'employee_id': self.employee.id,
        })
        payslip._onchange_employee()
        self.assertTrue(payslip, "test create payslip done.")
        payslip.compute_sheet()

        payslip.action_payslip_done()
        self.assertEqual(payslip.state, 'done',
                         "test confirm payslip change state to `Done`.")
