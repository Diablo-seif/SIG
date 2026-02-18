""" Initialize Res Company """

from odoo import fields, models


class ResCompany(models.Model):
    """
        Inherit Res Company:
        add responsible for payment request
    """
    _inherit = 'res.company'

    payment_request_responsible_id = fields.Many2one('res.users')
