""" init object resource.calendar.flexible"""

from odoo import fields, models


class ResourceCalendarFlexible(models.Model):
    """ init object resource.calendar.flexible"""
    _name = 'resource.calendar.flexible'
    _description = "Resource Calendar Flexible"

    name = fields.Char(string="Title", required=True)
    allow_attend_before_schedule = fields.Boolean()
    allowed_from_midday = fields.Boolean(default=True)
    allowed_from = fields.Float()
    allow_attend_after_schedule = fields.Boolean(default=True)
    allowed_to_midday = fields.Boolean(default=True)
    allowed_to = fields.Float()
    day_hours = fields.Float(string="Minimum number of hours per day",
                             default=8.0)
