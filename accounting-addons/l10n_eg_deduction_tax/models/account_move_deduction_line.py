"""Define Account move deduction line"""

from odoo import api, fields, models


class DeductionLine(models.Model):
    """
    init account.move.deduction.line
    define deduction lines to add calculated deduction taxes of invoice
    """
    _name = 'account.move.deduction.line'
    _description = 'Account Move Deduction Line'

    deduction_tax_id = fields.Many2one('account.tax', string='Tax Allowance')
    base_amount = fields.Monetary()
    tax_amount = fields.Monetary()
    total_amount = fields.Monetary()
    move_id = fields.Many2one('account.move')
    tax_amount_in_company_currency = fields.Monetary(
        compute='_compute_tax_amount_in_company_currency',
        store=True, currency_field='company_currency_id')
    paid_amount = fields.Monetary()
    paid_percentage = fields.Float(
        compute='_compute_residual_amount', store=True)
    currency_id = fields.Many2one(
        'res.currency', store=True, related='move_id.currency_id')
    company_currency_id = fields.Many2one(
        'res.currency', store=True, related='move_id.company_currency_id')
    residual_amount = fields.Monetary(
        compute='_compute_residual_amount', store=True)

    @api.depends('tax_amount', 'paid_amount')
    def _compute_residual_amount(self):
        """
        compute residual amount of deduction depends on
        tax_amount and paid_amount
        """

        for line in self:
            line.residual_amount = line.tax_amount - line.paid_amount
            if line.tax_amount:
                line.paid_percentage = (line.paid_amount /
                                        line.tax_amount) * 100
            else:
                line.paid_percentage = 0

    @api.depends('currency_id', 'company_currency_id', 'tax_amount',
                 'move_id.date')
    def _compute_tax_amount_in_company_currency(self):
        """
        compute tax amount in company currency from tax amount
        at bill/invoice date
        """
        for line in self:
            if line.move_id.date and line.currency_id:
                # pylint: disable=protected-access
                line.tax_amount_in_company_currency = line.currency_id._convert(
                    line.tax_amount, line.company_currency_id,
                    line.move_id.company_id, line.move_id.date)
            else:
                line.tax_amount_in_company_currency = 0
