""" inherit res.currency"""
from odoo import fields, models


class ResCurrency(models.Model):
    """
    inherit res.currency to translate unit label fields
    """
    _inherit = 'res.currency'

    currency_unit_label = fields.Char(translate=True)
    currency_subunit_label = fields.Char(translate=True)
