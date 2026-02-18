""" Initialize Account Journal """

from odoo import fields, models


class AccountJournal(models.Model):
    """
        Inherit Account Journal:
    """
    _inherit = 'account.journal'

    submit_einvoice = fields.Boolean('Submit E-Invoice')
    einvoice_purpose = fields.Selection(
        [('testing', 'Testing'), ('production', 'Production')],
        string='E-Invoice Purpose')
    einvoice_version = fields.Selection(
        [('0.9', '0.9'), ('1.0', '1.0')], string='E-Invoice Version',
        default='0.9')
    client_id = fields.Char()
    client_secret = fields.Char()
    min_individual_vat_amount = fields.Float(
        string='Min Amount required for individual to send ID', default=50000)
