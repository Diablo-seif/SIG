""" Initialize Access Tags """
from random import randint

from odoo import fields, models


class AccessTags(models.Model):
    """
        Initialize Access Tags:
         -
    """
    _name = 'access.tags'
    _description = 'Employee Access Tags'
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
