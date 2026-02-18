""" Integration Test for HR Job """
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestHrJob(TransactionCase):
    """ Unit Test for hr_job model """

    def test_name_get(self):
        """ Test Scenario: test name_get() """
        job = self.env.ref('hr.job_marketing')
        contract_type = self.env.ref('hr_contract_type.full_time_contract')
        level = self.env['hr.job.level'].create({
            'name': 'Senior',
            'level': '1',
            'schema': 'staff',
        })
        job.job_level_id = level.id
        job.contract_type_id = contract_type.id
        job_name = \
            job.with_context(**{'job_with_contract_type': True}).name_get()
        self.assertEqual(
            job_name, [(job.id, '%(level_name)s %(name)s '
                                '%(contract_type_name)s' % {
                                    "level_name": level.name,
                                    "name": job.name,
                                    "contract_type_name":
                                        ('[%s]' % contract_type.name)
                                })]
        )
        job_name = job.name_get()
        self.assertEqual(job_name, [(job.id, '%s %s' % (level.name, job.name))])

        with self.assertRaises(ValidationError):
            job.salary_type = 'range'
            job.min_salary = 500
            job.max_salary = 100
