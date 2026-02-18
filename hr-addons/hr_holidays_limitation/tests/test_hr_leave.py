""" Test HR Leave """
from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestHrLeave(TransactionCase):
    """ Test for test_hr_leave model """

    def setUp(self):
        """ Setup testing environment """
        super(TestHrLeave, self).setUp()
        self.hr_demo = self.env.ref('base.user_demo')
        contract = self.env.ref('hr_contract.hr_contract_fme')
        contract.date_end = fields.Date.today() + relativedelta(years=1)
        contract.date_start = fields.Date.today()
        contract.employee_id = self.env.ref('hr.employee_qdp')
        contract.employee_id.contract_id = contract.id
        contract.time_off_limitation = True
        self.hr_demo.groups_id = [
            (4, self.env.ref('hr_holidays.group_hr_holidays_user').id),
            (3, self.env.ref('hr_holidays.group_hr_holidays_manager').id)
        ]
        self.paid = self.env.ref('hr_holidays.holiday_status_cl')
        self.paid.no_of_days = 2
        self.paid.contract_limitation = 90
        self.comp = self.env.ref('hr_holidays.holiday_status_comp')
        self.comp.no_of_hours = 3

    def test_check_limitation(self):
        """ Test Scenario: test _check_limitation() """
        with self.assertRaises(ValidationError):
            with Form(self.env['hr.leave'].with_user(self.hr_demo.id)) as \
                    leave_form:
                leave_form.holiday_status_id = self.paid
                leave_form.request_date_from = fields.Date.today()
                leave_form.request_date_to = fields.Date.today()
            leave_form.save()
        with self.assertRaises(ValidationError):
            with Form(self.env['hr.leave'].with_user(self.hr_demo.id)) as \
                    leave_form:
                leave_form.holiday_status_id = self.comp
                leave_form.request_date_from = fields.Date.today()
                leave_form.request_date_to = fields.Date.today()
            leave_form.save()
        with self.assertRaises(ValidationError):
            self.paid.no_of_days = 0
            with Form(self.env['hr.leave'].with_user(self.hr_demo.id)) as \
                    leave_form:
                leave_form.holiday_status_id = self.paid
                leave_form.request_date_from = fields.Date.today()
                leave_form.request_date_to = fields.Date.today()
            leave_form.save()
