""" init object hr.leave.type"""

from odoo import fields, models


class HrLeaveType(models.Model):
    """ init object hr.leave.type"""
    _inherit = 'hr.leave.type'

    category = fields.Selection([('holiday', 'Holiday')], default="holiday",
                                tracking=True, )
