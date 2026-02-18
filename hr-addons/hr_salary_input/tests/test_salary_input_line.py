"""Integrated Tests for salary.input"""

from odoo.exceptions import ValidationError
from . import test_hr_contract


class TestSalaryInput(test_hr_contract.TestHrContract):
    """Integrated Tests"""

    def test_happy_scenario(self):
        """test Scenario: Happy scenario"""
        salary_input = self.env['salary.input.line'].create({
            'name': self.salary_input1.id,
            'date_from': '2018-01-02',
            'date_to': '2019-12-29',
            'contract_id': self.contract.id
        })
        self.assertTrue(salary_input, "NO salary input created")

    def test00_validate_line_dates(self):
        """test Scenario: Date to and not date from """
        with self.assertRaises(ValidationError):
            self.env['salary.input.line'].create({
                'name': self.salary_input1.id,
                'date_from': False,
                'date_to': '2018-01-02',
                'contract_id': self.contract.id
            })

    def test01_validate_line_dates(self):
        """test Scenario: Date to Greater then Contract Date end"""
        with self.assertRaises(ValidationError):
            self.env['salary.input.line'].create({
                'name': self.salary_input1.id,
                'date_from': '2018-01-01',
                'date_to': '2020-02-02',
                'contract_id': self.contract.id
            })

    def test02_validate_line_dates(self):
        """test Scenario: Date From but not date to"""
        with self.assertRaises(ValidationError):
            self.env['salary.input.line'].create({
                'name': self.salary_input1.id,
                'date_from': '2018-01-01',
                'date_to': False,
                'contract_id': self.contract.id
            })

    def test03_validate_line_dates(self):
        """test Scenario: Date From Greater than date to"""
        with self.assertRaises(ValidationError):
            self.env['salary.input.line'].create({
                'name': self.salary_input1.id,
                'date_from': '2020-02-02',
                'date_to': '2018-01-01',
                'contract_id': self.contract.id
            })

    def test04_validate_line_dates(self):
        """test Scenario: Date From LESS than contract date start"""
        with self.assertRaises(ValidationError):
            self.env['salary.input.line'].create({
                'name': self.salary_input1.id,
                'date_from': '2017-01-01',
                'date_to': '2017-02-02',
                'contract_id': self.contract.id
            })

    def test05_validate_line_dates(self):
        """test Scenario: Date Overlapping lines """
        with self.assertRaises(ValidationError):
            self.env['salary.input.line'].create({
                'name': self.salary_input1.id,
                'date_from': '2018-01-01',
                'date_to': '2019-01-01',
                'contract_id': self.contract.id
            })
            self.env['salary.input.line'].create({
                'name': self.salary_input1.id,
                'date_from': '2018-06-01',
                'date_to': '2019-06-02',
                'contract_id': self.contract.id
            })

    def test06_validate_line_dates(self):
        """test Scenario: No dates Overlapping lines """
        with self.assertRaises(ValidationError):
            self.env['salary.input.line'].create({
                'name': self.salary_input1.id,
                'date_from': False,
                'date_to': False,
                'contract_id': self.contract.id
            })
            self.env['salary.input.line'].create({
                'name': self.salary_input1.id,
                'date_from': False,
                'date_to': False,
                'contract_id': self.contract.id
            })
