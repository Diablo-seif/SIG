""" Initialize Res Partner Bank """

from odoo import fields, models


class ResPartnerBank(models.Model):
    """
        Inherit Res Partner Bank:
    """
    _inherit = 'res.partner.bank'

    iban = fields.Char(string='IBAN')
