""" Test Model """
from odoo import SUPERUSER_ID, api
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


# pylint: disable=protected-access
@tagged('post_install', '-at_install')
class PostTestModel(TransactionCase):
    """
    Integration test for testing model
    After adding x_approval_category_id field
    """
    def test_register_hook_after_install(self):
        """ Test Scenario: test register_hook() """
        env = api.Environment(self.env.cr, SUPERUSER_ID, {})
        model_list = list(env.values())
        magic_field = 'x_approval_category_id'
        for model in model_list:
            if model._auto:
                self.assertIn(magic_field, model.fields_get_keys())
