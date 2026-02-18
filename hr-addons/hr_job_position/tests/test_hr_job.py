""" Integration Test for HR Job """

from odoo.tests.common import TransactionCase


class TestHrJob(TransactionCase):
    """ Unit Test for hr_job model """

    def test_name_get(self):
        """ Test Scenario: test name_get() """
        job = self.env.ref('hr.job_developer')
        level = self.env['hr.job.level'].create({
            'name': 'Senior',
            'level': '1',
            'schema': 'staff',
        })
        job.job_level_id = level.id
        job_name = job.name_get()
        self.assertEqual(
            job_name, [(job.id, '%s %s' % (level.name or '', job.name or ''))]
        )
