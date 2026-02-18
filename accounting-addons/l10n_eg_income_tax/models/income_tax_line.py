"""init income tax line"""

from odoo import fields, models


class IncomeTaxLine(models.Model):
    """
    init income tax line as historical report
    """
    _name = 'income.tax.line'
    _description = "Income Tax Line"

    year = fields.Integer(required=True)
    net_profit = fields.Monetary(readonly=True)
    accounting_depreciation = fields.Monetary(readonly=True)
    above_seven = fields.Monetary(readonly=True, string="above 7%")
    tax_base = fields.Monetary(readonly=True)
    tax_depreciation = fields.Monetary(readonly=True)
    base = fields.Monetary(readonly=True)
    deferred_losses = fields.Monetary(readonly=True)
    base_after_losses = fields.Monetary(readonly=True)
    income_tax = fields.Monetary(readonly=True)
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='company_id.currency_id'
    )
