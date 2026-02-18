"""Integrated Tests for Leave"""

from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo.tests.common import TransactionCase


# pylint: disable=too-many-instance-attributes
class TestHrLeave(TransactionCase):
    """Integrated Tests"""

    # pylint: disable=invalid-name
    def setUp(self):
        """Setup the testing environment."""
        super(TestHrLeave, self).setUp()
        # Usefull models
        self.leave_model = self.env['hr.leave']
        self.user_demo_id = self.env.ref("base.user_demo").id
        self.employee_demo_id = self.env.ref("hr.employee_qdp").id
        self.excuse = self.env.ref("hr_leaves_excuse.hr_holidays_status_excuse")

    # pylint: disable=attribute-defined-outside-init
    def test_01_excuse_request_flow(self):
        """ Test excuse request flow """
        date_from = datetime.today() + relativedelta(months=4, days=1)
        date_to = date_from + relativedelta(hours=2)
        self.request_1 = self.leave_model.with_user(self.user_demo_id).create({
            'name': 'excuse001',
            'employee_id': self.employee_demo_id,
            'leave_category': "excuse",
            'holiday_status_id': self.excuse.id,
            'date_from': date_from.strftime("%Y-%m-%d %H:%M:%S"),
            'request_unit_hours': True,
            'date_to': date_to.strftime("%Y-%m-%d %H:%M:%S"),
            'state': 'draft',
            'number_of_days': 1,
        })
        self.request_1.sudo().action_confirm()
        self.request_1.sudo().action_approve()
