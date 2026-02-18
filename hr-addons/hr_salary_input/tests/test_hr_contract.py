"""Integrated Tests for hr.contract"""

from odoo.tests.common import TransactionCase


class TestHrContract(TransactionCase):
    """Integrated Tests"""

    def setUp(self):
        super(TestHrContract, self).setUp()
        input_obj = self.env['salary.input']
        employee_obj = self.env['hr.employee']
        contract_obj = self.env['hr.contract']
        self.salary_input1 = input_obj.create({
            'name': "Sample salary input #1",
            'code': 'Code00'
        })
        self.salary_input2 = input_obj.create({
            'name': "Sample salary input #2",
            'code': 'Code01'
        })
        self.employee = employee_obj.create({'name': 'Sample employee #1'})
        self.contract = contract_obj.create({
            'name': "Sample contract #1",
            'employee_id': self.employee.id,
            'wage': 1,
            'date_start': '2018-01-01',
            'date_end': '2020-01-01'
        })

    def test00_get_salary_inputs(self):
        """test Scenario: get salary inputs """
        input_line1 = self.env['salary.input.line'].create({
            'name': self.salary_input1.id,
            'date_from': '2018-03-01',
            'date_to': '2018-03-30',
            'code': self.salary_input1.code,
            'value': 20,
            'contract_id': self.contract.id
        })
        input_line2 = self.env['salary.input.line'].create({
            'name': self.salary_input2.id,
            'date_from': '2018-03-01',
            'date_to': '2018-03-30',
            'code': self.salary_input2.code,
            'value': 30,
            'contract_id': self.contract.id
        })
        self.assertTrue(input_line1, "line must be created.")
        self.assertTrue(input_line2, "line must be created.")
        input_sum1 = self.contract.get_salary_inputs(
            '2018-03-03', ['Code00']
        )
        input_sum2 = self.contract.get_salary_inputs(
            '2018-03-03', ['Code01']
        )
        input_sum_all = self.contract.get_salary_inputs('2018-03-03')
        self.assertEqual(input_sum1, 20, "salary inputs must be equal zero.")
        self.assertEqual(input_sum2, 30, "salary inputs must be equal zero.")
        self.assertEqual(input_sum_all, 50, "salary inputs must be equal zero.")
