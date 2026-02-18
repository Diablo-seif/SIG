"""Integrated Tests for hr.payslip.run"""

from odoo.tests.common import TransactionCase


class TestHrPayslipRun(TransactionCase):
    """Integrated Tests"""

    def setUp(self):
        """Setup the testing environment."""
        super(TestHrPayslipRun, self).setUp()
        self.employee_id = self.env['hr.employee'].create(
            {
                'name': 'Sample employee #55',
            }
        )
        self.contract_id = self.env['hr.contract'].create(
            {
                'name': 'Sample Contract for employee #55',
                'wage': 5000,
                'state': 'open',
                'date_start': '2019-01-01',
                'employee_id': self.employee_id.id,
            }
        )
        self.payslip_id = self.env['hr.payslip'].create(
            {'name': "Sample Payslip #55",
             'employee_id': self.employee_id.id,
             'date_from': '2020-01-01',
             'date_to': '2020-01-30', }
        )
        self.payslip_id.compute_sheet()

    def test00_export_payslip_batche(self):
        """test Scenario: test payslip batche action"""
        payslip_run_id = self.env['hr.payslip.run'].create(
            {'name': "Sample Payslip run #1",
             'slip_ids': [(6, 0, [self.payslip_id.id])]}
        )

        action = payslip_run_id.export_payslip_batche()
        self.assertEqual(action['type'],
                         'ir.actions.act_url',
                         "type must be equal ir.actions.act_url.")
