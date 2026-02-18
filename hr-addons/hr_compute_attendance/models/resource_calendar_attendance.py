""" init object resource.calendar.attendance"""

from odoo import fields, models


class ResourceCalendarAttendance(models.Model):
    """ init object resource.calendar.attendance"""
    _inherit = 'resource.calendar.attendance'

    flexible_id = fields.Many2one(comodel_name="resource.calendar.flexible",
                                  string="Flexibility")
