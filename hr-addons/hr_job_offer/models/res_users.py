""" Res Users """

from odoo import fields, models


class ResUsers(models.Model):
    """ inherit Res Users to ad signature """
    _inherit = 'res.users'

    sign_signature = fields.Binary()
