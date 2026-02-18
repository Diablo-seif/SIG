"""Integrated Tests for object hr Job Level"""

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestHrJobLevel(TransactionCase):
    """ Unit test for object hr job level """

    def setUp(self):
        """ Setup testing environment """
        super(TestHrJobLevel, self).setUp()
        self.env['res.config.settings'].sudo().create({
            'organization_levelling': 3
        }).execute()
        self.hr_manager = self.env.ref('base.user_admin')
        self.job_level = self.env['hr.job.level'].with_user(self.hr_manager.id)

    def test_check_levels(self):
        """
            test Scenario: test create hr job level
        """

        with self.assertRaises(ValidationError):
            for level in range(4):
                self.job_level.create({
                    'name': 'level%s' % level,
                    'level': '0%s' % level,
                    'code': level,
                    'schema': 'staff'
                })
