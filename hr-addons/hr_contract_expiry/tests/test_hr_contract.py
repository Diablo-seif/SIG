"""Integrated Tests for TestContractExpiry"""

from datetime import date

from dateutil.relativedelta import relativedelta

from odoo import _
from odoo.tests.common import TransactionCase

ERROR_MASSAGE = _('You can not have 2 contract that overlaps on same day')


# pylint: disable=too-many-instance-attributes
class TestContractExpiry(TransactionCase):
    """Integrated Tests"""

    # pylint: disable=invalid-name
    def setUp(self):
        """Setup the testing environment."""
        super(TestContractExpiry, self).setUp()
        # Usefull models
        self.HrEmployee = self.env['hr.employee']
        self.ResUsers = self.env['res.users']
        self.HrContract = self.env['hr.contract']
        no_reset = {'no_reset_password': True}
        # Groups
        self.group_hr_manager = self.env.ref('hr.group_hr_manager').id
        self.group_hr_contract_manager = self.env.ref('hr_contract.group_hr_'
                                                      'contract_manager').id

        # USERS
        user_hr_manager_values = {
            'name': 'Hr Manager Sample',
            'login': 'hr_manager',
            'email': 'hr_manager@test.com',
            'groups_id': [
                (6, 0, [
                    self.group_hr_manager,
                    self.group_hr_contract_manager,
                ])]
        }
        self.user_hr_manager = self.ResUsers.with_context(**no_reset).create(
            user_hr_manager_values
        )

        self.employee = self.HrEmployee.with_user(self.user_hr_manager).create({
            'name': 'Sample Employee #1'
        })
        self.now_date = date.today()

    def create_contract(self, date_start, date_end=False):
        """
        Function To create contract to tests
        :param date_start:
        :param date_end:
        :return:
        """
        values = {
            'name': 'Sample Contract #1',
            'employee_id': self.employee.id,
            'date_start': date_start,
            'wage': 4000,
        }
        if date_end:
            values.update(date_end=date_end)
        return self.HrContract.with_user(self.user_hr_manager).create(values)

    def test_01_contract_expiry(self):
        """
        Test Scenario: create contract with alert number = 1
        """
        before_6_months = self.now_date + relativedelta(months=-6)
        after_10_days = self.now_date + relativedelta(days=10)
        contract = self.create_contract(before_6_months, after_10_days)
        self.assertEqual(contract.alert_number, 1)

    def test_02_contract_expiry(self):
        """
        Test Scenario: create contract with alert number = 2
        """
        before_6_months = self.now_date + relativedelta(months=-6)
        after_40_days = self.now_date + relativedelta(months=1, days=10)
        contract = self.create_contract(before_6_months, after_40_days)
        self.assertEqual(contract.alert_number, 2)

    def test_03_contract_expiry(self):
        """
        Test Scenario: create contract with alert number = 3
        """
        before_6_months = self.now_date + relativedelta(months=-6)
        after_70_days = self.now_date + relativedelta(months=2, days=10)
        contract = self.create_contract(before_6_months, after_70_days)
        self.assertEqual(contract.alert_number, 3)

    def test_04_contract_expiry(self):
        """
        Test Scenario: create contract with alert number = 9
        """
        before_6_months = self.now_date + relativedelta(months=-6)
        after_4_months = self.now_date + relativedelta(months=4)
        contract = self.create_contract(before_6_months, after_4_months)
        self.assertEqual(contract.alert_number, 9)

    def test_05_contract_expiry(self):
        """
        Test Scenario: create contract with alert number = 10
        """
        before_6_months = self.now_date + relativedelta(months=-6)
        contract = self.create_contract(before_6_months)
        self.assertEqual(contract.alert_number, 10)
