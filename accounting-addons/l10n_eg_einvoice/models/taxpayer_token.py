""" Initialize Taxpayer Token """

from odoo import fields, models


class TaxpayerToken(models.Model):
    """
        Initialize Taxpayer Token:
    """
    _name = 'taxpayer.token'
    _description = 'Taxpayer Token'
    _check_company_auto = True

    access_token = fields.Text()
    expire_date = fields.Datetime()
    company_id = fields.Many2one(comodel_name='res.company', required=True,
                                 default=lambda self: self.env.company)
    client_id = fields.Char()
    client_secret = fields.Char()
    url = fields.Char()
