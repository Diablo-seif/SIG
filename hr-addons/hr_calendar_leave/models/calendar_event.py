""" init object calendar.event """

from odoo import fields, models


class CalendarEvent(models.Model):
    """ init object calendar.event """

    _inherit = 'calendar.event'

    auto_create_leave = fields.Boolean(
        string="Auto Create Time Off",
        help="Check To Add Time Off Automatically "
             "When Employee accept the attend for this meeting."
    )
