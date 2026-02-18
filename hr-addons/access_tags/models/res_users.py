""" Initialize Res Users """

from odoo import fields, models


class ResUsers(models.Model):
    """
        Inherit Res Users:
         -
    """
    _inherit = 'res.users'

    access_tags_ids = fields.Many2many(
        'access.tags'
    )
