"""Integrated Tests for object hr.payslip.run"""
from odoo import fields
from odoo.tests.common import TransactionCase


class TestHrPayslipRun(TransactionCase):
    """Integrated Tests"""

    def setUp(self):
        """Setup the testing environment."""
        super(TestHrPayslipRun, self).setUp()
        # Useful models
        self.users_obj = self.env['res.users']
        self.employee_obj = self.env['hr.employee']
        self.batch_obj = self.env['hr.payslip.run']
        self.payslip_obj = self.env['hr.payslip']
        # USERS
        self.manager_user = self.users_obj.create({
            'name': 'Hr Payroll Manager #3',
            'login': 'hrpmanager003@example.com',
            'email': 'hepmanager003@example.com',
            'groups_id': [(6, 0, [self.env.ref("hr_payroll."
                                               "group_hr_payroll_manager").id])]
        })
        self.employees = self.env['hr.employee'].search([
            ('contract_id', '!=', False),
            ('contract_id.structure_type_id', '!=', False)], limit=5)

    # pylint: disable=protected-access
    def generate_payslips(self, batch, date_from, date_to):
        """
        Generate Payslips for payslip batch for employees
        """
        payslip_ids = self.payslip_obj
        for employee in self.employees:
            values = {
                'name': employee.name,
                'employee_id': employee.id,
                'date_from': date_from,
                'date_to': date_to,
                'payslip_run_id': batch.id,
            }
            payslip = self.payslip_obj.with_user(
                self.manager_user.id).create(values)
            payslip._onchange_employee()
            if payslip.contract_id:
                payslip_ids |= payslip
        return payslip_ids

    def test00_send_batch_payslip(self):
        """test Scenario: send payslip batch by mail. """
        date_start = fields.Datetime.now().replace(day=1).date()
        date_end = fields.Datetime.now().replace(day=20).date()
        date_start = fields.Date.to_string(date_start)
        date_end = fields.Date.to_string(date_end)
        values = {
            'name': 'Sample Payslip Batch #1',
            'date_start': date_start,
            'date_end': date_end,
        }
        batch = self.batch_obj.with_user(self.manager_user.id).create(values)
        self.generate_payslips(batch, date_start, date_end)
        self.assertTrue(batch.slip_ids, 'cannot generate payslips for batch.')
        self.assertEqual(batch.payslip_count, len(self.employees),
                         'payslip count must be equal number of employees.')
        batch.compute_payslips()
        batch.action_confirm()
        self.assertEqual(batch.state, "confirmed",
                         "the batch status must be confirmed.")
        res = batch.action_open_payslips()
        expected_domain_res = [['id', 'in', batch.slip_ids.ids]]
        self.assertEqual(res['domain'], expected_domain_res,
                         "domain not matched with result returned.")
