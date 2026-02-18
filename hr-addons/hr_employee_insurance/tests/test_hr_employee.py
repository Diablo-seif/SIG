""" Test HR Employee """

from datetime import date

from dateutil.relativedelta import relativedelta

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestHrEmployee(TransactionCase):
    """ Test for hr_employee model """

    # pylint: disable=protected-access
    def test_employee_insurance(self):
        """ Test Scenario: test employee insurance"""
        employee = self.env.ref('hr.employee_hne')
        insur_mngr = self.env.ref('base.user_admin')
        insur_mngr.groups_id = [(4, self.env.ref(
            'l10n_eg_social_insurance.group_social_insurance_manager').id)]
        insurance_obj = self.env['employee.insurance.history'].with_user(
            insur_mngr.id)
        insurance_history = insurance_obj.create({
            'company': 'company1',
            'employee_id': employee.id,
            'date_from': date(date.today().year - 3, 1, 1),
            'date_to': date(date.today().year - 3, 12, 31)
        })
        date_difference = relativedelta(
            insurance_history.date_to + relativedelta(days=1),
            insurance_history.date_from
        )
        self.assertEqual(
            insurance_history.duration_days,
            date_difference.days
        )
        self.assertEqual(
            insurance_history.duration_months,
            date_difference.months
        )
        self.assertEqual(
            insurance_history.duration_years,
            date_difference.years
        )
        with self.assertRaises(ValidationError):
            insurance_obj.create({
                'company': 'company2',
                'employee_id': employee.id,
                'date_from': date(date.today().year - 3, 1, 1),
                'date_to': date(date.today().year - 3, 12, 31)
            })
