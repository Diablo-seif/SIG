""" Initialize Uom """

from odoo import fields, models


class UomUom(models.Model):
    """
        Inherit Uom Uom:
    """
    _inherit = 'uom.uom'

    code = fields.Char()
