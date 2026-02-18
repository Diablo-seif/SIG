""" Initialize Account Move Line """

from odoo import _, fields, models, api
from odoo.exceptions import ValidationError


# pylint: disable=no-member,protected-access,no-self-use
from odoo.tools import float_compare


class AccountMoveLine(models.Model):
    """
        Inherit Account Move Line:
    """
    _inherit = 'account.move.line'

    tax_group_sequence = fields.Integer(related='tax_group_id.sequence',
                                        store=True)

    def _get_line_qty(self):
        """  Get Line Qty """
        self.ensure_one()
        return self.quantity

    def _get_taxes_res(self, price_subtotal, currency, partner, move_type):
        self.ensure_one()
        res = self.tax_ids._origin.compute_all(
            price_subtotal,
            quantity=1.0, currency=currency, product=self.product_id,
            partner=partner, is_refund=move_type in ('out_refund', 'in_refund'))
        taxes = res.get('taxes')
        nontaxable_amount = 0
        taxable_items = []
        for tax in taxes:
            tax_id = self.env['account.tax'].browse(tax.get('id'))
            if not tax_id.is_taxable:
                nontaxable_amount += tax.get('amount')
            if tax_id.is_taxable:
                taxable_items.append({
                    "taxType": tax_id.tax_group_id.code,
                    "amount": self.round_number(abs(tax.get('amount'))),
                    "subType": tax_id.code,
                    "rate": abs(tax_id.amount),
                })

        res.update({
            'nontaxable_amount': abs(nontaxable_amount),
            'taxable_items': taxable_items
        })
        return res

    def _get_line_unit_value(self, qty, subtotal_currency, subtotal_base):
        """  Get Line unit value """
        self.ensure_one()
        amount = subtotal_base / qty
        rate = 0
        amount_sold = 0
        if float_compare(subtotal_base, subtotal_currency, precision_digits=5):
            rate = subtotal_base / subtotal_currency
            amount_sold = amount / rate
        return {
            "currencySold": self.currency_id.name,
            "amountEGP": self.round_number(amount),
            "amountSold": self.round_number(amount_sold),
            "currencyExchangeRate": self.round_number(rate)}

    @api.model
    def round_number(self, amount):
        """ return number in 5 digits only """
        return round(amount, 5)

    def einvoice_data(self):
        """ preparw invoice lines data """
        lines = []
        self._einvoice_validate_data()
        for line in self:
            qty = line._get_line_qty()
            move = line.move_id
            subtotal_currency = self.round_number(line.price_subtotal)
            subtotal_base = self.round_number(line.debit + line.credit)
            unit_price = self.round_number(subtotal_base / qty)
            unit_price_currency = self.round_number(subtotal_currency / qty)
            subtotal_base = unit_price * qty
            subtotal_currency = unit_price_currency * qty
            tax_res = line._get_taxes_res(subtotal_base,
                                          line.company_currency_id,
                                          move.partner_id,
                                          move.move_type)
            lines.append({
                "description": line.name,
                "itemType": line.product_id.global_product_classification_type,
                "itemCode": line.product_id.global_product_classification,
                "unitType": line.product_uom_id.code,
                "quantity": qty,
                "internalCode": line.product_id.default_code,
                "salesTotal": self.round_number(tax_res.get('total_excluded')),
                "total": self.round_number(tax_res.get('total_included')),
                "itemsDiscount":
                    self.round_number(tax_res.get('nontaxable_amount')),
                "valueDifference": 0.0,
                "totalTaxableFees": 0.0,
                "netTotal": self.round_number(tax_res.get('total_excluded')),
                "unitValue": line._get_line_unit_value(
                    qty, subtotal_currency, self.round_number(tax_res.get('total_excluded'))),
                "taxableItems": tax_res.get('taxable_items', [])
            })
        return lines

    def _einvoice_validate_data(self):
        for line in self:
            product_name = line.product_id.name or line.name
            if not line.product_id.global_product_classification_type:
                raise ValidationError(
                    _('Missing global product classification type for %s') %
                    product_name)
            if not line.product_id.global_product_classification:
                raise ValidationError(
                    _('Missing global product classification for %s') %
                    product_name)
            if not line.product_uom_id.code:
                raise ValidationError(
                    _('Missing UOM code for %s') % product_name)
            if not line.product_id.default_code:
                raise ValidationError(
                    _('Missing internal reference for %s') % product_name)
            if line._get_line_qty() <= 0:
                raise ValidationError(
                    _('Quantity must more than 0 for %s') % product_name)
            if not all(line.mapped('tax_ids.code')):
                raise ValidationError(
                    _('Missing tax code for %s') % product_name)
            if not all(line.mapped('tax_ids.tax_group_id.code')):
                raise ValidationError(
                    _('Missing tax group code for %s') % product_name)
