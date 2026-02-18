""" Initialize account.einvoice.outgoing """

from odoo import fields, models


class AccounteDocumentReceive(models.Model):
    """ record invoice / refund / debit note received from vendor via ETA """
    _name = 'account.document.receive'
    _description = 'Egypt E-Invoice Vendor Bill / Refund'
    _order = 'id desc'
    _rec_name = 'invoice_uuid'

    invoice_uuid = fields.Char(required=True)
    invoice_number = fields.Char()
    invoice_submit_uuid = fields.Char()
    state = fields.Selection(
        string='Status', selection=[('new', 'New'), ('created', 'Created')],
        required=True, default="new")
