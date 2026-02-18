""" Integration Test Action Reason """
from odoo.tests.common import TransactionCase


class TestActionReason(TransactionCase):
    """ Unit Test for Action Reason model """
    # pylint: disable=protected-access
    def test_action_reason(self):
        """ Test Scenario: test _compute_model() """
        model = self.env.ref('action_reason.model_action_reason')
        reason1 = self.env['action.reason'].sudo().create({
            'name': 'Reason',
            'model_id': model.id,
        })
        self.assertEqual(reason1.res_model, model.model)

        reason2 = self.env['action.reason'].sudo().new({
            'name': 'Reason2',
            'res_model': 'action.reason',
        })
        reason2._inverse_model()
        self.assertEqual(reason2.model_id.model, reason2.res_model)
