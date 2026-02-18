""" Initialize Res Partner """

from odoo import fields, models


class ResPartner(models.Model):
    """
        Inherit Res Partner:
    """
    _inherit = 'res.partner'

    payment_request_line_ids = fields.One2many('payment.request.line',
                                               'partner_id')
