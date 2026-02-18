""" init object res.company"""

from odoo import fields, models


class ResCompany(models.Model):
    """ init object res.company"""
    _inherit = 'res.company'

    calendar_leave_type_id = fields.Many2one(comodel_name="hr.leave.type",
                                             string="Calendar Time Off Type")
