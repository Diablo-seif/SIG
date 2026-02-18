"""Integrated Tests for object res config settings"""

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestResConfigSettings(TransactionCase):
    """ Unit test for object res config settings """
    def test_validate_organization_levelling(self):
        """ test Scenario: test create res config settings """
        with self.assertRaises(ValidationError):
            self.env['res.config.settings'].sudo().create({
                'organization_levelling': -1
            })
