""" This Module add Branch to employee """

from odoo import fields, models


class HrEmployee(models.Model):
    """ HR Employee Model """
    _inherit = 'hr.employee'

    branch_id = fields.Many2one('res.branch', string="Work Branch",
                                groups="hr.group_hr_user")
