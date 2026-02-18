""" Initialize Res Branch Tag """

from random import randint

from odoo import fields, models


class ResBranchTag(models.Model):
    """
        Initialize Res Branch Tag:
         -
    """
    _name = 'res.branch.tag'
    _description = 'Branch Tag'
    _check_company_auto = True

    name = fields.Char(
        required=True,
        translate=True,
    )
    color = fields.Integer(
        default=lambda self: randint(1, 11)
    )
    active = fields.Boolean(
        default=True
    )
