""" init object calendar.attendee """

from dateutil.relativedelta import relativedelta

from odoo import SUPERUSER_ID
from odoo import api, fields, models


class CalendarAttendee(models.Model):
    """ init object calendar.attendee """

    _inherit = 'calendar.attendee'

    # pylint: disable=arguments-differ
    @api.model
    def create(self, values):
        """
        Override create to add leaves.
        :param values:
        """
        res = super(CalendarAttendee, self).create(values)
        if self.env.user.partner_id in res.mapped('partner_id'):
            # pylint: disable=protected-access
            res._create_leaves()
        return res

    def _remove_leaves(self):
        """
        Remove Time Off from Attendees
        """
        leave_attendee_ids = self.filtered(
            lambda rec: rec.leave_id and rec.leave_id.state in ['draft'])
        if leave_attendee_ids:
            leave_ids = leave_attendee_ids.mapped('leave_id')
            leave_ids.unlink()
            leave_attendee_ids.write({'leave_id': False})

    def _prepare_timeoff(self, employee_id, leave_type_id, event_id,
                         date_to):
        """
        Prepare the dict of values to create the new timeoff for a employee.

        :param employee_id: object: hr.employee
        :param leave_type_id: object: hr.leave.type
        :param event_id: object: calendar.event
        :param date_to: datetime
        """
        self.ensure_one()
        vals = {
            'employee_id': employee_id.id,
            'holiday_status_id': leave_type_id.id,
            'date_from': event_id.start,
            'date_to': date_to,
            'name': event_id.name or "Auto Calendar Event",
        }
        return vals

    # pylint: disable=protected-access
    def _create_leaves(self):
        """
        Create Time Off
        """
        leave_type_id = self.env.company.calendar_leave_type_id
        if leave_type_id:
            for rec in self:
                event_id = rec.event_id
                date_from = event_id.start
                date_to = False
                employee_id = False
                if date_from and event_id.duration and not event_id.allday:
                    date_to = date_from + relativedelta(
                        hours=event_id.duration)
                # get the user from the partner using admin
                user_id = self.env['res.users'].with_user(SUPERUSER_ID).search(
                    [('partner_id', '=', rec.partner_id.id)], limit=1)
                if user_id:
                    # get employee From user
                    employee_ids = user_id.employee_ids
                    if employee_ids:
                        employee_id = user_id.employee_ids[0]
                if employee_id \
                        and date_to \
                        and not rec.leave_id \
                        and rec.event_id.auto_create_leave:
                    leave_id = self.env['hr.leave'].with_user(
                        SUPERUSER_ID).\
                        create(rec._prepare_timeoff(
                            employee_id, leave_type_id, event_id, date_to))
                    rec.with_user(SUPERUSER_ID).update(
                        {'leave_id': leave_id.id}
                    )

    # pylint: disable=no-member
    def do_tentative(self):
        """ Override To remove leave. """
        self._remove_leaves()
        return super(CalendarAttendee, self).do_tentative()

    # pylint: disable=no-member
    def do_decline(self):
        """ Override To remove leave. """
        self._remove_leaves()
        return super(CalendarAttendee, self).do_decline()

    # pylint: disable=no-member
    def do_accept(self):
        """ Override To Add leave when event invitation is Accepted. """
        res = super(CalendarAttendee, self).do_accept()
        self._create_leaves()
        return res

    leave_id = fields.Many2one(comodel_name="hr.leave", string="Time Off")
