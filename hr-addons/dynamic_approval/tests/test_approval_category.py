""" Test Model """
from odoo.tests.common import TransactionCase


# pylint: disable=protected-access
class TestApprovalCategory(TransactionCase):
    """ Integration test for approval_category """

    def test_create_model_relation(self):
        """ Test Scenario: test create_model_relation """
        approval_category = self.env.ref(
            'approvals.approval_category_data_general_approval')
        model = self.env.ref('approvals.model_approval_request')
        action = self.env.ref(
            'approvals.approval_request_action_to_review_category')
        validated_action_ctx = approval_category.validate_context(
            approval_category.context)

        approval_category.model_id = model.id
        # Check that _onchange_model_id
        # will return correct domain and reset the action
        expected_domain = {'domain': {
            'action_id': [('res_model', '=', model.model)]
        }}
        domain = approval_category._onchange_model_id()
        self.assertEqual(domain, expected_domain)
        self.assertFalse(approval_category.action_id)
        approval_category.action_id = action.id
        self.env['approval.request'].create({
            'name': 'Test Request',
            'quantity': 10,
            'category_id': approval_category.id,
            'x_approval_category_id': approval_category.id,
        })
        request_action = approval_category.create_request()
        self.assertEqual(request_action['context'], validated_action_ctx)
        request_action = approval_category.view_request()
        self.assertEqual(request_action['context'], validated_action_ctx)
        self.assertEqual(
            request_action['domain'],
            [('x_approval_category_id', '=', approval_category.id)]
        )
        self.assertEqual(approval_category.request_to_validate_count, 1)
