"""Integrated Tests for object hr.payslip"""
# pylint: disable=import-error
from odoo.addons.hr_payroll.tests.common import TestPayslipBase

from odoo import fields


# pylint: disable=invalid-name
class TestHrPayslip(TestPayslipBase):
    """Integrated Tests"""

    def setUp(self):
        """Setup the testing environment"""
        super(TestHrPayslip, self).setUp()
        self.manager_user = self.env['res.users'].create({
            'name': 'Hr Payroll Manager #1',
            'login': 'hrpmanager001@example.com',
            'email': 'hepmanager001@example.com',
            'groups_id': [(6, 0, [self.env.ref("hr_payroll."
                                               "group_hr_payroll_manager").id])]
        })
        self.payslipObj = self.env['hr.payslip'].with_user(self.manager_user.id)
        self.employee = self.env.ref('hr.employee_admin')

    # pylint: disable=protected-access
    def test00_send_payslip(self):
        """test Scenario: send payslip by mail. """
        date_from = fields.Date.today().replace(day=1)
        date_to = fields.Date.today().replace(day=25)
        payslip = self.payslipObj.create({
            'name': 'November 2015',
            'employee_id': self.employee.id,
            'date_from': date_from,
            'date_to': date_to, })
        payslip._onchange_employee()
        self.assertTrue(payslip, "payslip cannot be created by manager user.")
        payslip.action_payslip_send_only()
        self.assertTrue(payslip.mark_payslip_as_sent,
                        "payslip cannot be marked as send.")
        res = payslip[0].action_payslip_send()
        self.assertIsInstance(res, dict, "the result must be a dictionary.")
