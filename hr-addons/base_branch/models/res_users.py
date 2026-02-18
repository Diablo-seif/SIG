""" Inherit Res Users """

from odoo import fields, models


class ResUsers(models.Model):
    """
        Inherit Res Users:
         - add user company branch
    """
    _inherit = 'res.users'

    branch_id = fields.Many2one('res.branch', check_company=True)
