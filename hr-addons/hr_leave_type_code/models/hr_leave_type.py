""" Inherit hr.leave.type """

from odoo import fields, models

class HrLeaveType(models.Model):
    """
        inherit hr.leave.type:
    """
    _inherit = 'hr.leave.type'

    code = fields.Char("Payroll Code")  
