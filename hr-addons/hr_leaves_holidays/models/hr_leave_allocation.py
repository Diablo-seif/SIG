""" init object hr.leave.allocation"""

from odoo import fields, models


class HrLeaveAllocation(models.Model):
    """ init object hr.leave.allocation"""
    _inherit = 'hr.leave.allocation'

    leave_category = fields.Selection([('holiday', 'Holiday')],
                                      default="holiday",
                                      tracking=True, string="Time Off Category")
