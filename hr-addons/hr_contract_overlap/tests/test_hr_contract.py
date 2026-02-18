"""Integrated Tests for TestContractOverlaps"""

from datetime import datetime

from odoo import _
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase

ERROR_MASSAGE = _('You can not have 2 contract that overlaps on same day')


# pylint: disable=too-many-instance-attributes
class TestContractOverlaps(TransactionCase):
    """Integrated Tests"""

    # pylint: disable=invalid-name
    def setUp(self):
        """Setup the testing environment."""
        super(TestContractOverlaps, self).setUp()
        # Useful models
        self.ResUsers = self.env['res.users']
        self.HrContract = self.env['hr.contract']
        self.HrEmployee = self.env['hr.employee']
        no_reset = {'no_reset_password': True}
        # Groups
        self.group_hr_contract_manager = self.env.ref(
            'hr_contract.group_hr_contract_manager').id
        self.group_hr_manager = self.env.ref('hr.group_hr_manager').id
        # USERS
        user_hr_manager_values = {
            'name': 'Sample Hr Manager',
            'login': 'hr_manager',
            'email': 'hr_manager@example.com',
            'groups_id': [
                (6, 0, [
                    self.group_hr_contract_manager,
                    self.group_hr_manager,
                ])]
        }
        self.user_hr_manager = self.ResUsers.with_context(**no_reset).create(
            user_hr_manager_values)

        self.employee = self.HrEmployee.with_user(self.user_hr_manager).create({
            'name': 'Sample Employee #1'
        })

    def create_contract(self, date_start, date_end):
        """
        Function To create contract to tests
        :param date_start:
        :param date_end:
        :return:
        """
        if date_start and isinstance(date_start, str):
            date_start = datetime.strptime(date_start, "%Y-%m-%d")
        if date_end and isinstance(date_end, str):
            date_end = datetime.strptime(date_end, "%Y-%m-%d")
        values = {
            'name': 'Sample Contract #1',
            'employee_id': self.employee.id,
            'wage': 1000,
            'date_start': date_start
        }
        if date_end:
            values.update(date_end=date_end)
        return self.HrContract.with_user(self.user_hr_manager).create(values)

    def test_01_contract_overlaps(self):
        """
        Test Scenario: not accepted create contract
        form 2018-01-01 to 2018-02-01.
        when create contract orm 2018-02-01 to 2018-02-28.
        """
        contract2 = self.create_contract('2018-02-01', '2018-02-28')
        self.assertTrue(contract2, "test create contract "
                                   "form 2018-02-01 to 2018-02-28 done.")

        with self.assertRaisesRegex(UserError, ERROR_MASSAGE):
            self.create_contract('2018-01-01', '2018-02-01')

    def test_02_contract_overlaps(self):
        """
        Test Scenario:not accepted create contract form 2018-01-01 to Open
        when create contract orm 2018-02-01 to 2018-02-28.
        """

        contract2 = self.create_contract('2018-02-01', '2018-02-28')
        self.assertTrue(contract2, "test create contract "
                                   "form 2018-02-01 to 2018-02-28 done.")

        with self.assertRaisesRegex(UserError, ERROR_MASSAGE):
            self.create_contract('2018-01-01', False)

    def test_03_contract_overlaps(self):
        """
        Test Scenario: not accepted create contract
        form 2018-02-28 to 2018-03-31
        when create contract orm 2018-02-01 to 2018-02-28
        """

        contract2 = self.create_contract('2018-02-01', '2018-02-28')
        self.assertTrue(contract2, "test create contract "
                                   "form 2018-02-01 to 2018-02-28 done.")

        with self.assertRaisesRegex(UserError, ERROR_MASSAGE):
            self.create_contract('2018-02-25', '2018-03-31')

    def test_04_contract_overlaps(self):
        """
        Test Scenario: accepted create contract
        form 2018-01-31 to 2018-01-31
        and form 2018-03-01 to 2018-03-31
        and form 2018-04-01 to Open
        when create contract orm 2018-02-01 to 2018-02-28
        """

        contract2 = self.create_contract('2018-02-01', '2018-02-28')
        self.assertTrue(contract2, "test create contract "
                                   "form 2018-02-01 to 2018-02-28 done.")

        contract1 = self.create_contract('2018-01-01', '2018-01-31')
        self.assertTrue(contract1, "test create contract "
                                   "form 2018-01-01 to 2018-01-31 done.")
        contract3 = self.create_contract('2018-03-01', '2018-03-31')
        self.assertTrue(contract3, "test create contract "
                                   "form 2018-03-01 to 2018-03-31 done.")

        contract7open = self.create_contract('2018-07-01', False)
        self.assertTrue(contract7open, "test create contract "
                                       "form 2018-07-01 to Open done.")

    def test_05_contract_overlaps(self):
        """
        Test Scenario: not accepted create contract
        form 2018-01-01 to open
        when create contract orm 2018-05-01 to Open
        """

        contract5 = self.create_contract('2018-05-01', False)
        self.assertTrue(contract5, "test create contract "
                                   "form 2018-05-01 to Open done.")

        with self.assertRaisesRegex(UserError, ERROR_MASSAGE):
            self.create_contract('2018-01-01', False)

    def test_06_contract_overlaps(self):
        """
        Test Scenario: not accepted create contract
        form 2018-05-01 to open
        when create contract orm 2018-05-01 to Open
        """

        contract5 = self.create_contract('2018-05-01', False)
        self.assertTrue(contract5, "test create contract "
                                   "form 2018-05-01 to Open done.")

        with self.assertRaisesRegex(UserError, ERROR_MASSAGE):
            self.create_contract('2018-05-01', False)

    def test_07_contract_overlaps(self):
        """
        Test Scenario: not accepted create contract
        form 2018-04-01 to 2018-05-01
        when create contract orm 2018-05-01 to Open
        """

        contract5 = self.create_contract('2018-05-01', False)
        self.assertTrue(contract5, "test create contract "
                                   "form 2018-05-01 to Open done.")

        with self.assertRaisesRegex(UserError, ERROR_MASSAGE):
            self.create_contract('2018-05-01', '2018-05-01')

    def test_08_contract_overlaps(self):
        """
        Test Scenario: accepted create contract
        form 2018-04-01 to 2018-04-30
        when create contract orm 2018-05-01 to Open
        """

        contract5 = self.create_contract('2018-05-01', False)
        self.assertTrue(contract5, "test create contract "
                                   "form 2018-05-01 to Open done.")

        contract4 = self.create_contract('2018-04-01', '2018-04-30')
        self.assertTrue(contract4, "test create contract "
                                   "form 2018-05-01 to 2018-04-30 done.")
