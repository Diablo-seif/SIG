""" Test Enroll Form """
from num2words import num2words

from odoo import fields
from odoo.tests.common import TransactionCase


class TestEnrollForm(TransactionCase):
    """ Integration test for test_enroll_form model """

    def setUp(self):
        """ Setup testing environment """
        super().setUp()
        self.demo_user = self.env.ref('base.user_demo')
        self.demo_user.groups_id = [(4, self.env.ref(
            'l10n_eg_social_insurance.group_social_insurance_manager').id)]
        self.date = fields.Date.today()
        self.emp1 = self.env.ref('hr.employee_admin')
        self.emp1.write({
            'employee_insurance_number': '123456789',
            'insured_salary': 1200,
            'insurance_history_ids': [(0, 0, {
                'date_from': self.date.replace(day=1, month=1),
                'insurance_salary': 1200,
                'company': 'test',
            })]
        })
        self.emp2 = self.env.ref('hr.employee_qdp')
        self.emp2.write({
            'employee_insurance_number': '134679741',
            'insured_salary': 8000
        })
        self.emp3 = self.env.ref('hr.employee_al')
        self.emp3.write({
            'employee_insurance_number': '165146541',
            'insured_salary': 2000
        })

    def create_social_insurance_config(self):
        """ helper function to create insurance configuration"""
        self.env['social.insurance.config'].create({
            'method': 'percentage',
            'value': 15,
            'min_value': 1000,
            'max_value': 7000,
            'date_from': self.date.replace(day=1, month=1),
            'date_to': self.date.replace(day=31, month=12),
        })

    # pylint: disable=too-many-arguments
    def create_insurance_enroll_form(self, active_ids, date, method, amount,
                                     round_value=False):
        """ Helper function to create enroll form """
        enroll_form_wizard = self.env['create.enroll.form'].with_context(
            active_ids=active_ids).create({'date': date,
                                           'method': method,
                                           'amount': amount})
        if round_value:
            enroll_form_wizard.round_value = round_value
        enroll_form_wizard.create_enroll_form()

    def test_00_create_enroll_form(self):
        """ Test Scenario: test enroll form creation with percentage
         and with configuration min / max
         """
        self.create_social_insurance_config()
        active_ids = [self.emp1.id, self.emp2.id, self.emp3.id]
        date = self.date.replace(day=1, month=2)
        self.create_insurance_enroll_form(active_ids, date, 'percentage', 15,
                                          100)
        enroll_form = self.env['hr.insurance.enroll.form'].search([])
        self.assertEqual(enroll_form.form_date, self.date.replace(
            day=1, month=2))

    def test_01_create_enroll_form(self):
        """ Test Scenario: test enroll form creation with fixed
         and with configuration min / max
         """
        self.create_social_insurance_config()
        active_ids = [self.emp1.id, self.emp2.id, self.emp3.id]
        date = self.date.replace(day=2, month=2)
        self.create_insurance_enroll_form(active_ids, date, 'fixed', 100)
        enroll_form = self.env['hr.insurance.enroll.form'].search([])
        self.assertEqual(enroll_form.form_date, self.date.replace(
            day=2, month=2))

    def test_02_create_enroll_form(self):
        """ Test Scenario: test enroll form creation without
         configuration min / max
         """
        active_ids = [self.emp1.id, self.emp2.id, self.emp3.id]
        date = self.date.replace(day=2, month=2)
        self.create_insurance_enroll_form(active_ids, date, 'fixed', 100)
        enroll_form = self.env['hr.insurance.enroll.form'].search([])
        self.assertEqual(enroll_form.form_date, self.date.replace(
            day=2, month=2))

    def test_03_confirm_enroll_form(self):
        """ Test Scenario: confirm enroll form with increase is fixed
        and check for effect in employee profile and insurance history """
        active_ids = [self.emp1.id]
        date = self.date.replace(day=2, month=2)
        self.create_insurance_enroll_form(active_ids, date, 'fixed', 100)
        enroll_form = self.env['hr.insurance.enroll.form'].search([])
        enroll_form.action_confirm()
        self.assertEqual(self.emp1.insured_salary, 1300)

        new_history = self.emp1.insurance_history_ids.filtered(
            lambda r: not r.date_to)
        self.assertEqual(new_history.date_from, date)
        self.assertEqual(new_history.insurance_salary, 1300)

    def test_04_confirm_enroll_form(self):
        """ Test Scenario: confirm enroll form with increase is percentage
        and check for effect in employee profile and insurance history """
        active_ids = [self.emp1.id, self.emp3.id]
        date = self.date.replace(day=2, month=2)
        self.create_insurance_enroll_form(active_ids, date, 'percentage', 10)
        enroll_form = self.env['hr.insurance.enroll.form'].search([])
        enroll_form.action_confirm()
        self.assertEqual(self.emp1.insured_salary, 1320)
        emp1_history = self.emp1.insurance_history_ids.filtered(
            lambda r: not r.date_to)
        self.assertEqual(emp1_history.date_from, date)
        self.assertEqual(emp1_history.insurance_salary, 1320)

        self.assertEqual(self.emp3.insured_salary, 2200)
        emp3_history = self.emp3.insurance_history_ids.filtered(
            lambda r: not r.date_to)
        self.assertEqual(emp3_history.insurance_salary, 2200)

    def test_05_cancel_enroll_form(self):
        """ Test Scenario: cancel enroll form """
        active_ids = [self.emp1.id]
        date = self.date.replace(day=2, month=2)
        self.create_insurance_enroll_form(active_ids, date, 'percentage', 10)
        enroll_form = self.env['hr.insurance.enroll.form'].search([])
        enroll_form.action_cancel()
        self.assertEqual(enroll_form.state, 'canceled')

    def test_06_set_draft_enroll_form(self):
        """ Test Scenario: draft enroll form """
        active_ids = [self.emp1.id]
        date = self.date.replace(day=1, month=3)
        self.create_insurance_enroll_form(active_ids, date, 'percentage', 12)
        enroll_form = self.env['hr.insurance.enroll.form'].search([])
        enroll_form.action_cancel()
        enroll_form.action_draft()
        self.assertEqual(enroll_form.state, 'draft')

    def test_07_employee_count(self):
        """ Test Scenario: check for count of employees """
        active_ids = [self.emp3.id]
        date = self.date.replace(day=1, month=4)
        self.create_insurance_enroll_form(active_ids, date, 'percentage', 20)
        enroll_form = self.env['hr.insurance.enroll.form'].search([])
        count_label = num2words(1, lang='ar').title()
        self.assertEqual(enroll_form.employees_count, count_label)
