""" init vat department """

from odoo import models, fields


class VatDepartment(models.Model):
    """inherit res.partner to add tax details"""
    _name = 'vat.department'
    _description = 'VAT Department'

    name = fields.Char(
        required=True,
    )
    active = fields.Boolean(
        default=True,
    )
    code = fields.Char(
        required=True,
    )
