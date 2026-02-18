""" init object res.config.settings"""

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    """ init object  res.config.settings"""
    _inherit = 'res.config.settings'

    calendar_leave_type_id = fields.Many2one(
        comodel_name="hr.leave.type",
        string="Calendar Time Off Type",
        related="company_id.calendar_leave_type_id",
        readonly=False,
        help="Time Off Type Added Automatically when "
             "Calendar Attendance Approved."
    )
