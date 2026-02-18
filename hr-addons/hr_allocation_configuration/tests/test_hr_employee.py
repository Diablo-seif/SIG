""" Test HR Employee """
from datetime import date

from odoo.tests.common import TransactionCase


class TestHrEmployee(TransactionCase):
    """ Test for test_hr_employee model """

    def test_employee_insurance(self):
        """ Test Scenario: test employee_insurance() """

        employee = self.env.ref('hr.employee_hne')
        employee.birthday = date(date.today().year-60, 1, 1)
        employee.insurance_history_ids = [(0, 0, {
            'company': 'company1',
            'employee_id': employee.id,
            'date_from': date(date.today().year-10, 1, 1),
            'date_to': date.today()
        })]
        insurance_years = sum(
            employee.mapped('insurance_history_ids.insurance_days')
        ) / 365
        self.assertEqual(employee.total_insurance_years, int(insurance_years))
        self.env['hr.employee'].check_employee_insurance()
        self.assertEqual(employee.insurance_checked, True)
        self.assertTrue(employee.activity_ids)
