""" Integrated Test for HR Job """
from odoo.tests.common import TransactionCase


class TestHrJob(TransactionCase):
    """  Unit test for hr_job model """

    def test_get_job_description(self):
        """
            Test Scenario: test that job position description
            is equal to job description template description
        """
        group_hr_user = self.env.ref('hr.group_hr_user')
        hr_employee = self.env.ref('base.user_demo')
        hr_employee.groups_id = [(4, group_hr_user.id)]
        job_position = self.env.ref('hr.job_consultant')
        job_description_template = self.env[
            'hr.job.description.template'].with_user(hr_employee).create({
                'name': 'Template',
                'job_description': 'job Description',
            })
        job_position.job_description_template_id = job_description_template.id
        self.assertEqual(job_position.website_description,
                         job_description_template.job_description)
