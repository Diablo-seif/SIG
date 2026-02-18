""" HR Leave Type Tag """

from odoo import _, fields, models


class HrLeaveTypeTag(models.Model):
    """ HR Leave Type Tag"""
    _name = 'hr.leave.type.tag'

    allocation_tag_id = fields.Many2one("hr.allocation.tag", required=True)
    number_of_days = fields.Float(string="Number of days/Year", required=True)
    leave_type_id = fields.Many2one("hr.leave.type")

    _sql_constraints = [(
        'unique_tag',
        'unique(allocation_tag_id, leave_type_id)',
        _("Tag Can't be duplicated")
    )]
