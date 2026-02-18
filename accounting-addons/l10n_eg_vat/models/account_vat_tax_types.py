""" account.vat.tax.types"""
from odoo import fields, models


class AccountVatTaxTypes(models.Model):
    """
    account.vat.tax.types
    """
    _name = 'account.vat.tax.types'
    _description = "VAT Tax Types"
    _order = "name"

    name = fields.Char(translate=True)
    description = fields.Char(translate=True)
    code = fields.Integer()
    invoice_type = fields.Selection(selection=[
        ('out', 'Customer Invoice'),
        ('in', 'Vendor Bill')], string='Scope')
    tax_type = fields.Selection([('vat', 'VAT'),
                                 ('table1', 'Table 1'),
                                 ('table2', 'Table 2')])
