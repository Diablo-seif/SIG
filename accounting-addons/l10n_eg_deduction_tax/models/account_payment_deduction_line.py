""" define account.payment.deduction.line model"""

from odoo import fields, models


class AccountPaymentDeductionLine(models.Model):
    """ define account.payment.deduction.line model"""
    _name = "account.payment.deduction.line"
    _description = "Deduction Lines on Payment"

    deduction_tax_id = fields.Many2one('account.tax')
    base_amount = fields.Monetary()
    tax_amount = fields.Monetary()
    total_amount = fields.Monetary()
    # pylint: disable=attribute-string-redundant
    tax_percentage = fields.Float(
        related="deduction_tax_id.amount", store=True, string='Tax Percentage')
    payment_id = fields.Many2one('account.payment')
    currency_id = fields.Many2one(
        'res.currency', store=True, related='payment_id.currency_id')
    tax_type = fields.Selection(store=True, related='payment_id.tax_type')
