""" HR Leave Type Tags """

from odoo import fields, models


# pylint: disable=no-self-use,inconsistent-return-statements
class HrLeaveType(models.Model):
    """ HR Leave Type """
    _inherit = 'hr.leave.type'

    tag_ids = fields.One2many("hr.leave.type.tag", "leave_type_id")
