""" HR Leave Type """
from odoo import fields, models


class HrLeaveType(models.Model):
    """ inherit HR Leave Type to add limitation option"""
    _inherit = 'hr.leave.type'

    contract_limitation = fields.Integer(
        help='No. Of days to allow request time off before based on contract'
    )
    no_of_days = fields.Integer(
        help='No. Of days to allow request time off before'
    )
    no_of_hours = fields.Integer(
        help='No. Of hours to allow request time off before'
    )
