""" init account.einvoice.token.log """
from odoo import fields, models


class AccountEInvoiceTokenLog(models.Model):
    """ init account.einvoice.token.log """
    _name = 'account.einvoice.token.log'
    _description = 'Egypt E-Invoice Token Log'
    _order = 'id desc'

    request_url = fields.Char(required=True)
    request_method = fields.Char(required=True)
    request_header = fields.Text(required=True, default='{}')
    request_data = fields.Text(required=True, default='{}')
    request_params = fields.Text(required=True, default='{}')
    result = fields.Text(copy=False)


