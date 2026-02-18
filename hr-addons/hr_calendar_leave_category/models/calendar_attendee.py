""" init object calendar.attendee """

from odoo import models


# pylint: disable=no-member
class CalendarAttendee(models.Model):
    """ init object calendar.attendee """

    _inherit = 'calendar.attendee'

    def _prepare_timeoff(self, employee_id, leave_type_id, event_id, date_to):
        """
        override to add type category

        :param employee_id: object: hr.employee
        :param leave_type_id: object: hr.leave.type
        :param event_id: object: calendar.event
        :param date_to: datetime
        """
        res = super()._prepare_timeoff(
            employee_id, leave_type_id, event_id, date_to)
        res.update({'leave_category': leave_type_id.category})
        return res
