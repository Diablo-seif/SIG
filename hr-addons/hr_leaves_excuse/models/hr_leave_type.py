""" init object hr.leave.type"""

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class HrHolidaysStatus(models.Model):
    """ init object hr.leave.type"""
    _inherit = 'hr.leave.type'

    category = fields.Selection(selection_add=[('excuse', 'Excuse')],
                                ondelete={'excuse': 'set default'})
    max_excuse_times = fields.Integer("No. of Excuses per month")
    max_excuse_hours_per_month = fields.Float(
        "No. Of hours per month excuse",
    )

    @api.constrains('max_excuse_times', 'max_excuse_hours_per_month')
    def _check_max_excuse_bandwidth(self):
        """
        Function to check the number of max excuse times and
        number of max excuse per time is zero or posative numbers
        """
        if self.max_excuse_times < 0 or self.max_excuse_hours_per_month < 0:
            raise UserError(_("The number can't be negative"))
