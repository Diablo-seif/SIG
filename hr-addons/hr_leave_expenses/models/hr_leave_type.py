""" init object hr.leave.type"""

from odoo import fields, models


class HrLeaveType(models.Model):
    """ init object hr.leave.type"""
    _inherit = 'hr.leave.type'

    link_to_expenses = fields.Boolean()
    leave_expense_ids = fields.One2many("hr.leave.expense", "leave_type_id",
                                        string="Time Off Expense Lines", )
