""" init object hr.leave"""

from odoo import fields, models


class HrHolidays(models.Model):
    """ init object hr.leave"""
    _inherit = 'hr.leave'

    leave_category = fields.Selection(selection_add=[('mission', 'Mission')],
                                      ondelete={'mission': 'set default'}
                                      )
