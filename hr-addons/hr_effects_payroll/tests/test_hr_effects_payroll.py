"""Integrated Tests for effect payroll"""

from datetime import date

from psycopg2 import IntegrityError

from odoo import _
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


# pylint: disable=too-many-instance-attributes
class TestHrEffectsPayroll(TransactionCase):
    """Integrated Tests"""

    # pylint: disable=invalid-name
    def setUp(self):
        """Setup the testing environment."""
        super(TestHrEffectsPayroll, self).setUp()
        # Usefull models
        self.ResUsers = self.env['res.users']
        self.HrEmployee = self.env['hr.employee']
        self.HrEffectsPayroll = self.env['hr.effects.payroll']
        self.HrEffectsPayrollType = self.env['hr.effects.payroll.type']

        # Groups
        self.group_manage_effects = self.env.ref(
            'hr_effects_payroll.group_manage_hr_effects_payroll').id
        self.group_manage_effects_type = self.env.ref(
            'hr_effects_payroll.group_manage_hr_effects_payroll_type').id

        # USERS
        user_manage_effects_value = {
            'name': 'Sample User Manage Effects',
            'login': 'manage_effects',
            'email': 'manage_effects@example.com',
            'groups_id': [
                (6, 0, [self.group_manage_effects])]
        }
        self.user_manage_effects = self.ResUsers.with_context(
            **{'no_reset_password': True}).create(user_manage_effects_value)
        user_type_value = {
            'name': 'Sample User Manage Effects Category',
            'login': 'manage_effects_type',
            'email': 'manage_effects_type@example.com',
            'groups_id': [
                (6, 0, [self.group_manage_effects_type])]
        }
        self.user_manage_effects_type = self.ResUsers.with_context(
            **{'no_reset_password': True}).create(user_type_value)

        self.employee = self.HrEmployee.create({'name': 'Sample Employee #1'})

    # Tests Addition

    def _create_addition_category(self):
        """ create Addition Category """
        type_values = {
            'name': "Sample Addition Category #1",
            'effects_category': "additions",
            'code': "sample01",
        }
        return self.HrEffectsPayrollType.with_user(
            self.user_manage_effects_type).create(type_values)

    def _create_addition(self):
        """ create Addition """
        effects_values = {
            'employee_id': self.employee.id,
            'effects_category': "additions",
            'effects_type_id': self._create_addition_category().id,
            'effective_date': date.today(),
            'value': 1000.50,
        }
        return self.HrEffectsPayroll.with_user(self.user_manage_effects).create(
            effects_values)

    def test_01_create_additions_category(self):
        """Test Scenario: Create Addition Category."""
        addition_category = self._create_addition_category()
        self.assertTrue(addition_category,
                        "test create addition category done.")

    def test_02_create_additions(self):
        """Test Scenario: Create Addition."""
        addition = self._create_addition()
        self.assertTrue(addition, "test create addition done.")

    def test_03_additions_value_constraints(self):
        """Test Scenario: create additions value Constraints."""
        effects_values = {
            'employee_id': self.employee.id,
            'effects_category': "additions",
            'effects_type_id': self._create_addition_category().id,
            'effective_date': date.today(),
            'value': -1,
        }
        # SQL erros raise the constriant name not the message

        with self.assertRaisesRegex(IntegrityError, "positive_value"):
            self.HrEffectsPayroll.with_user(self.user_manage_effects).create(
                effects_values)

    def test_04_default_value_additions(self):
        """Test Scenario: create additions with Default Values."""
        addition = self._create_addition()
        self.assertEqual(addition.state, "draft",
                         "test default addition state is draft.")

    def test_05_delete_approved_additions(self):
        """Test Scenario: remove approved additions."""
        addition = self._create_addition()
        addition.state = "approved"
        self.assertEqual(addition.state, "approved",
                         "test change addition state to approved.")
        parameters = {'effects_category_str': _('Additions')}
        error_message = _('You Cannot Delete %(effects_category_str)s '
                          'in State Approved.') % parameters
        msg = 'test cannot remove approved addition'
        with self.assertRaisesRegex(UserError, error_message, msg=msg):
            addition.with_user(self.user_manage_effects).unlink()

    # Tests Deduction

    def _create_deduction_category(self):
        """ create Deduction Category """
        type_values = {
            'name': "Sample Deduction Category #1",
            'effects_category': "deductions",
            'code': "sample02",
        }
        return self.HrEffectsPayrollType.with_user(
            self.user_manage_effects_type).create(type_values)

    def _create_deduction(self):
        """ create Deduction """
        effects_values = {
            'employee_id': self.employee.id,
            'effects_category': "deductions",
            'effects_type_id': self._create_deduction_category().id,
            'effective_date': date.today(),
            'value': 1000.50,
        }
        return self.HrEffectsPayroll.with_user(self.user_manage_effects).create(
            effects_values)

    def test_101_create_deductions_category(self):
        """Test Scenario: Create Deduction Category."""
        deduction_category = self._create_deduction_category()
        self.assertTrue(deduction_category,
                        "test create deduction category done.")

    def test_102_create_deductions(self):
        """Test Scenario: Create Deduction."""
        deduction = self._create_deduction()
        self.assertTrue(deduction, "test create deduction done.")

    def test_103_deductions_value_constraints(self):
        """Test Scenario: create deductions value Constraints."""
        effects_values = {
            'employee_id': self.employee.id,
            'effects_category': "deductions",
            'effects_type_id': self._create_deduction_category().id,
            'effective_date': date.today(),
            'value': -1,
        }
        # SQL erros raise the constriant name not the message
        with self.assertRaisesRegex(IntegrityError,
                                    "positive_value"):
            self.HrEffectsPayroll.with_user(self.user_manage_effects).create(
                effects_values)

    def test_104_default_value_deductions(self):
        """Test Scenario: create deductions with Default Values."""
        deduction = self._create_deduction()
        self.assertEqual(deduction.state, "draft",
                         "test default deduction state is draft.")

    def test_105_delete_approved_deductions(self):
        """Test Scenario: remove approved deductions."""
        deduction = self._create_deduction()
        deduction.state = "approved"
        self.assertEqual(deduction.state, "approved",
                         "test change deduction state to approved.")
        parameters = {'effects_category_str': _('Deductions')}
        error_message = _('You Cannot Delete %(effects_category_str)s '
                          'in State Approved.') % parameters
        msg = 'test cannot remove approved deduction'
        with self.assertRaisesRegex(UserError, error_message, msg=msg):
            deduction.with_user(self.user_manage_effects).unlink()

    # Tests Effects function to used in payslip
    # pylint: disable=too-many-arguments
    def create_effects_by_values(self, employee, deduction_category,
                                 effective_date, value, approve):
        """
        Create Effects By Values
        :param employee:
        :param deduction_category:
        :param effective_date:
        :param value:
        :return: Hr.Effects.Payroll Object
        """
        deduction_effects_values = {
            'employee_id': employee.id,
            'effects_category': deduction_category.effects_category,
            'effects_type_id': deduction_category.id,
            'effective_date': effective_date,
            'value': value,
        }
        if approve:
            deduction_effects_values.update(state='approved')
        return self.HrEffectsPayroll.with_user(self.user_manage_effects).create(
            deduction_effects_values)

    def test_200_test_employee_deduction(self):
        """Test Scenariro: Test Employee Total Deduction Function."""

        deduction_category = self._create_deduction_category()

        self.create_effects_by_values(self.employee, deduction_category,
                                      '2018-01-01', 100, approve=True)
        self.create_effects_by_values(self.employee, deduction_category,
                                      '2018-02-01', 100, approve=True)
        self.create_effects_by_values(self.employee, deduction_category,
                                      '2018-02-05', 200, approve=True)
        self.create_effects_by_values(self.employee, deduction_category,
                                      '2018-02-15', 300, approve=True)
        self.create_effects_by_values(self.employee, deduction_category,
                                      '2018-02-28', 400, approve=True)
        self.create_effects_by_values(self.employee, deduction_category,
                                      '2018-02-28', 500, approve=False)

        # the total value deduction (2018-02-01 : 2018-02-28) should be -1000
        total_deduction = self.employee.get_effects_payroll(
            deduction_category.effects_category, '2018-02-01', '2018-02-28')
        self.assertEqual(total_deduction, -1000.00,
                         'test total deduction function in employee.')

    def test_201_test_employee_addition(self):
        """Test Scenariro: Test Employee Total Addition Function."""

        addition_category = self._create_addition_category()

        self.create_effects_by_values(self.employee, addition_category,
                                      '2018-01-01', 100, approve=True)
        self.create_effects_by_values(self.employee, addition_category,
                                      '2018-02-05', 100, approve=True)
        self.create_effects_by_values(self.employee, addition_category,
                                      '2018-02-15', 100, approve=True)
        self.create_effects_by_values(self.employee, addition_category,
                                      '2018-02-28', 100, approve=True)
        self.create_effects_by_values(self.employee, addition_category,
                                      '2018-02-28', 500, approve=False)

        # the total value addition (2018-02-01 : 2018-02-28) should be 300
        total_addition = self.employee.get_effects_payroll(
            addition_category.effects_category, '2018-02-01', '2018-02-28')
        self.assertEqual(total_addition, 300.00,
                         'test total addition function in employee.')
