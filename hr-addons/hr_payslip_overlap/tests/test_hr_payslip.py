"""Integrated Tests for object hr.payslip"""
# pylint: disable=import-error
from odoo.addons.hr_payroll.tests.common import TestPayslipBase

from odoo import _, fields
from odoo.exceptions import UserError


# pylint: disable=invalid-name
class TestHrPayslip(TestPayslipBase):
    """Integrated Tests"""

    def setUp(self):
        """Setup the testing environment."""
        super(TestHrPayslip, self).setUp()
        self.manager_user = self.env['res.users'].create({
            'name': 'Hr Payroll Manager #1',
            'login': 'hrpmanager001@example.com',
            'email': 'hepmanager001@example.com',
            'groups_id': [(6, 0, [self.env.ref("hr_payroll."
                                               "group_hr_payroll_manager").id])]
        })
        self.payslipObj = self.env['hr.payslip'].with_user(self.manager_user.id)

    def test00_create_tow_payslips(self):
        """test Scenario:
        Create tow payslips with the same duration and employee. """
        date_from = fields.Date.today().replace(day=1)
        date_to = fields.Date.today().replace(day=25)
        payslip = self.payslipObj.create({
            'name': 'November 2015',
            'employee_id': self.richard_emp.id,
            'date_from': date_from,
            'date_to': date_to,
            'contract_id': self.richard_emp.contract_id.id,
            'struct_id': self.developer_pay_structure.id,
        })
        self.assertTrue(payslip, "payslip cannot be created by manager user.")
        msg = "You cannot have two payslips that overlap " \
              "in duration for the same Employee."
        with self.assertRaisesRegex(UserError, _(msg)):
            payslip.copy()
