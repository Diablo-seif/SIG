""" Initialize Hr Leave Type """

from odoo import fields, models


class HrLeaveType(models.Model):
    """
        Inherit Hr Leave Type:
         - 
    """
    _inherit = 'hr.leave.type'

    allocation_type = fields.Selection(
        selection=[('by_overtime', 'By Overtime'),
                   ('accrual', 'Accrual'),
                   ('regular', 'Regular'),
                   ('fixed', 'Fixed')],
        # selection_add=[('by_overtime', 'By Overtime')]
    )
