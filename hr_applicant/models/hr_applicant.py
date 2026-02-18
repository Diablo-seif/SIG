""" Inherit hr.applicant """

from odoo import fields, models

class HrLeaveType(models.Model):
    """
        inherit hr.applicant:
    """
    _inherit = 'hr.applicant'

    test = fields.Char()
