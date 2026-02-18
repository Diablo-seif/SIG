""" HR Transfer Allocation """

from odoo import models


class HrLeaveAllocation(models.Model):
    """ inherit HR Leave Allocation """
    _inherit = 'hr.leave.allocation'
    _sql_constraints = [('duration_check', 'CHECK(1=1)', '')]
