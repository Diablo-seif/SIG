"""Integrated Tests for hr employee"""

from odoo.tests.common import TransactionCase


class TestHrEmployee(TransactionCase):
    """ Unit test for object hr employee """

    def setUp(self):
        """ Setup testing environment """
        super(TestHrEmployee, self).setUp()
        self.hr_manager = self.env.ref('base.user_admin')
        self.job_level = self.env['hr.job.level'].with_user(self.hr_manager.id)
        self.employee = self.env['hr.employee'].with_user(self.hr_manager.id)

    def test_get_employees_count(self):
        """
            test Scenario:
            -   test count of employee
        """
        number_of_employees = self.employee.search_count([
            ('job_level_id', '!=', False)])
        employees_groub_by_levels = self.employee.get_employees([])
        number_of_employees_in_levels = sum([len(l) for i, l in
                                             employees_groub_by_levels])
        self.assertEqual(number_of_employees_in_levels, number_of_employees)

    def test_get_employees_domain(self):
        """
            test Scenario:
            -   test get employee with domain
        """
        department = self.env['hr.department'].search([
            ('name', '=', 'Professional Services')])
        number_of_employees = self.employee.search_count([
            ('job_level_id', '!=', False),
            ('department_id', '=', department.id)])
        employees_groub_by_levels = self.employee.get_employees([
            ('department_id', '=', department.id)])
        number_of_employees_in_levels = sum([len(l) for i, l in
                                             employees_groub_by_levels])
        self.assertEqual(number_of_employees_in_levels, number_of_employees)

    def test_get_employees_schema(self):
        """
            test Scenario:
            -   test count of employee
        """
        number_of_employees = self.employee.search_count([
            ('job_level_id', '!=', False)])
        employees_groub_by_schema = self.employee.get_schema()
        number_of_employees_in_schema = sum([l[1] for i, l in
                                             employees_groub_by_schema])
        self.assertEqual(number_of_employees_in_schema, number_of_employees)
