"""Integrated Tests for calendar leave"""

from datetime import datetime, timedelta

from odoo.tests.common import TransactionCase


class TestCalendarTimeOff(TransactionCase):
    """Integrated Tests"""

    def setUp(self):
        """Setup the testing environment."""
        super(TestCalendarTimeOff, self).setUp()
        # USERS
        self.user1 = self.env.ref('base.user_admin')
        self.leave_type_id = self.env['hr.leave.type'].create({
            'name': 'Calendar TimeOff',
            'request_unit': 'hour',
            'allocation_type': 'no',
        })
        self.user1.company_id.calendar_leave_type_id = self.leave_type_id

    def test00_calendar_leave(self):
        """test Scenario: Create TimeOff When Attendee Event. """
        duration = 3
        # @formatter:off
        start = datetime(2020, 12, 7, 8, 0)
        stop = start + timedelta(minutes=duration * 60)
        event = self.env['calendar.event'].create(
            {'name': 'Sample Event #456',
             'partner_ids': [(4, self.user1.partner_id.id)],
             'start_date': start,
             'stop_date': stop,
             'start': start,
             'stop': stop,
             'duration': duration,
             'auto_create_leave': True,
             }
        )
        self.assertTrue(event.attendee_ids, "attendee records not created.")
        attendee = event.attendee_ids[0]
        attendee.do_accept()
        self.assertTrue(attendee.leave_id, "TimeOff must be created.")
        attendee.leave_id.state = "draft"
        attendee.do_decline()
        # just for increasing the coverage
        attendee.do_tentative()
        self.assertFalse(attendee.leave_id, "TimeOff must be deleted.")
