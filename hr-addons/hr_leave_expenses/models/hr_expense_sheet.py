""" init object hr.expense.sheet"""

from odoo import fields, models


class HrExpenseSheet(models.Model):
    """ init object  hr.expense.sheet"""
    _inherit = 'hr.expense.sheet'

    leave_id = fields.Many2one("hr.leave", string="Time Off", )
