""" Test HR Employee """
from odoo.tests.common import TransactionCase


class TestHrEmployee(TransactionCase):
    """ Test for test_hr_employee model """

    def test_create_employee_from_applicant(self):
        """ Test Scenario: test create_employee_from_applicant() """
        application = self.env.ref('hr_recruitment.hr_case_financejob1')
        application.create_employee_from_applicant()
        self.assertEqual(
            application.emp_id.contract_type_id,
            application.job_id.contract_type_id
        )
        self.assertEqual(
            application.emp_id.country_id,
            application.country_id
        )
