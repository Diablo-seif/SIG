""" Integration test for Test Hr Salary Tax """
from odoo.tests import Form, common


class TestHrSalaryTax(common.TransactionCase):
    """ Integration test for test_hr_salary_tax """

    def setUp(self):
        """ Setup testing environment """
        super(TestHrSalaryTax, self).setUp()
        self.employee = self.env.ref('hr.employee_admin')
        rule = self.env.ref('hr_salary_tax.net_before_tax_salary_rule')
        rule.amount_python_compute = 'result = payslip.paid_amount'
        tax = self.env['hr.salary.tax'].search([])
        if tax:
            tax.active = False
        self.tax = self.env['hr.salary.tax'].create({
            'exemption': 9000,
            'rounding': 10,
            'rounding_method': 'ceil',
            'date_from': '2019-7-01',
            'date_to': '2025-6-30',
            'salary_tax_line_ids': [
                (0, 0, {
                    'level': 1,
                    'salary_from': 0,
                    'salary_to': 8000,
                    'tax_percentage': 0,
                    'refund_percentage': 0,
                }), (0, 0, {
                    'level': 2,
                    'salary_from': 8000,
                    'salary_to': 30000,
                    'tax_percentage': 10,
                    'refund_percentage': 85,
                }), (0, 0, {
                    'level': 3,
                    'salary_from': 30000,
                    'salary_to': 45000,
                    'tax_percentage': 15,
                    'refund_percentage': 45,
                }), (0, 0, {
                    'level': 4,
                    'salary_from': 45000,
                    'salary_to': 200000,
                    'tax_percentage': 20,
                    'refund_percentage': 7.5,
                }), (0, 0, {
                    'level': 5,
                    'salary_from': 200000,
                    'salary_to': 999999999999,
                    'tax_percentage': 22.5,
                    'refund_percentage': 0,
                }),
            ],
        })

    def test_hr_salary_tax(self):
        """ Test Scenario: Hr Salary Tax """
        with Form(self.env['hr.payslip']) as payslip_form:
            payslip_form.employee_id = self.employee
            payslip_form.struct_id = self.env.ref(
                'l10n_eg_payroll.full_time_salary_structure')
        payslip = payslip_form.save()
        payslip.compute_sheet()
        # pylint: disable=protected-access
        self.assertTrue(payslip._get_salary_line_total('TAX'))
