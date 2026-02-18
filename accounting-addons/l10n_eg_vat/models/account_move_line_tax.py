"""inherit account move line tax"""

from odoo import fields, models


class AccountMoveLineTax(models.Model):
    """
    account move line tax
    to have tax amount per invoice line
    """
    _name = "account.move.line.tax"
    _description = "Account Move Line Tax"

    move_id = fields.Many2one('account.move')
    line_id = fields.Many2one('account.move.line')
    tax_id = fields.Many2one('account.tax')
    tax_amount = fields.Float()
    line_tax_one = fields.Boolean()
    vat_product_kind = fields.Integer()
