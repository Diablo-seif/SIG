""" init object hr.leave.allocation"""

from odoo import fields, models


class HrLeaveAllocation(models.Model):
    """ init object hr.leave.allocation"""
    _inherit = 'hr.leave.allocation'

    leave_category = fields.Selection(selection_add=[('mission', 'Mission')],
                                      ondelete={'mission': 'set default'})
