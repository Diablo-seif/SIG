""" init object hr.leave.type"""

from odoo import fields, models


class HrHolidaysStatus(models.Model):
    """ init object hr.leave.type"""
    _inherit = 'hr.leave.type'

    category = fields.Selection(selection_add=[('mission', 'Mission')],
                                ondelete={'mission': 'set default'})
