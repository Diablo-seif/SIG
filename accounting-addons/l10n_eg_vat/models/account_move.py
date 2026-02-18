"""inherit account move"""

from odoo import fields, models, api


class AccountMove(models.Model):
    """
    inherit account move
    to add fields for VAT
    """
    _inherit = "account.move"

    supplier_invoice_number = fields.Integer()
    tax_adjustment = fields.Boolean()
    tax_reported = fields.Boolean()
    tax_adjustment_year_month = fields.Integer()
    vat_tax_line_ids = fields.One2many(
        'account.move.line.tax',
        'move_id',
        string="VAT Taxes",
        compute='_compute_vat_tax_line_ids',
        store=True,
    )

    @api.depends('line_ids.price_subtotal', 'line_ids.tax_ids')
    def _compute_vat_tax_line_ids(self):
        """
        compute lines of vat taxes
        """
        # pylint: disable=too-many-nested-blocks
        for move in self:
            move.write({'vat_tax_line_ids': [(5, 0, 0)]})
            tax_line = self.env['account.move.line.tax']
            for line in move.invoice_line_ids.filtered(lambda ln: ln.tax_ids):
                price_unit_wo_discount = line.price_unit * (
                    1 - (line.discount / 100.0))
                taxes_res = line.tax_ids.compute_all(
                    price_unit_wo_discount,
                    quantity=line.quantity,
                    currency=line.currency_id,
                    product=line.product_id,
                    partner=line.partner_id,
                    is_refund=move.move_type in ('out_refund', 'in_refund'))
                if taxes_res['taxes']:
                    line_tax_one = True
                    for tax_line_invoice_line in taxes_res['taxes']:
                        tax_id = tax_line_invoice_line['id']
                        tax_amount = tax_line_invoice_line['amount']
                        tax_line_found = tax_line.search(
                            [('move_id', '=', move.id),
                             ('line_id', '=', line.id),
                             ('tax_id', '=', tax_id)])

                        # get the product kind code
                        product_kind = self.get_product_kind_code(tax_id, line)
                        if tax_line_found:
                            tax_line_found[0].write({
                                'tax_amount': tax_amount,
                                'vat_product_kind': product_kind
                            })
                        else:
                            tax_line.create({
                                'move_id': move.id,
                                'line_id': line.id,
                                'tax_id': tax_id,
                                'tax_amount': tax_amount,
                                'line_tax_one': line_tax_one,
                                'vat_product_kind': product_kind,
                            })
                        line_tax_one = False

    def get_product_kind_code(self, tax_id, line):
        """  get product kind code"""
        code = 0
        tax = self.env['account.tax'].browse(tax_id)
        table_tax_type = tax.tax_group_id.tax_group_type
        if tax.tax_group_id.tax_group_type == 'table':
            table_tax_type = tax.tax_group_id.table_tax_type

        for tax_type in line.account_vat_tax_types_ids:
            if table_tax_type == tax_type.tax_type:
                code = tax_type.code
                break
        return code

    def action_close_report(self, month, mark_as_reported, close_year):
        """  mark invoices as reported """
        active_ids = self.env.context.get('active_ids')
        call_model = self.env.context.get('report_model')

        if active_ids and call_model:
            move_ids = self.env[call_model].browse(
                active_ids).mapped('move_id').ids
            invoices = self.env['account.move'].browse(move_ids)
            reported = invoices.filtered(
                lambda invoice: (invoice.invoice_date.month == int(month) and
                                 invoice.invoice_date.year == close_year))
            reported.write({'tax_reported': mark_as_reported})
            adjustments = invoices.filtered(
                lambda invoice: (invoice.invoice_date.month < int(
                    month) and invoice.invoice_date.year == close_year) or (
                        invoice.invoice_date.year < close_year))
            if adjustments:
                if mark_as_reported:
                    tax_adjustment_year_month = int(str(
                        close_year) + month.rjust(2, '0'))
                else:
                    tax_adjustment_year_month = 0
                adjustments.write({
                    'tax_adjustment': mark_as_reported,
                    'tax_reported': mark_as_reported,
                    'tax_adjustment_year_month': tax_adjustment_year_month
                })
