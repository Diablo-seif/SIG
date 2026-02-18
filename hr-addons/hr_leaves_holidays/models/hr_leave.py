""" init object hr.leave"""

from odoo import api, fields, models


class HrHolidays(models.Model):
    """ init object hr.leave"""
    _inherit = 'hr.leave'

    # pylint: disable=no-self-use
    def _custom_leave_check(self):
        """
        Custom Time Off Check.
        :return: dict {state, response}
        """
        return {'state': True, 'response': 'Done'}

    # pylint: disable=no-member, attribute-defined-outside-init
    # pylint: disable=access-member-before-definition
    @api.onchange('leave_category')
    def _onchange_leave_category(self):
        """
        Onchange leave category change leave type if not same category.
        """
        if self.leave_category and self.holiday_status_id and \
                self.holiday_status_id.category != self.leave_category:
            self.holiday_status_id = False

    leave_category = fields.Selection([('holiday', 'Holiday')], tracking=True,
                                      string="Time Off Category",
                                      default="holiday",)
