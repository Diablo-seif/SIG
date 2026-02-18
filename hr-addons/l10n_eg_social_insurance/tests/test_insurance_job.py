""" Test Insurance Job """
from odoo import _
from odoo.tests.common import TransactionCase


class TestHrEmployee(TransactionCase):
    """ Test for Insurance Job """

    # pylint: disable=protected-access
    def test_insurance_job(self):
        """ Test Scenario: test insurance job """
        job = self.env['insurance.job'].create({
            'name': 'job 1',
            'code': '123456',
        })
        name_get = [(job.id, _("[%(code)s] %(name)s")
                     % {"code": job.code, "name": job.name})]
        # test name_get method
        self.assertEqual(job.name_get(), name_get)
        # test name_search method
        self.assertEqual(job.name_search(name='1234'), name_get)
