""" inherit account.tax"""
from odoo import fields, models


class AccountTax(models.Model):
    """
    inherit account.tax to translate name field
    and add deduction code for deduction report integration
    """
    _inherit = 'account.tax'

    name = fields.Char(translate=True)
    deduction_code = fields.Char()
    type_tax_deduction = fields.Selection(
        selection=[('withholding', 'Withholding'), ('deduction', 'Deduction')],
        string='Allowance Type')
    tax_type = fields.Selection(
        selection=[('tax', 'Tax'),
                   ('tax_withholding', 'Deduction/Withholding Tax')],
        default="tax", string="Tax/Allowance Type")
