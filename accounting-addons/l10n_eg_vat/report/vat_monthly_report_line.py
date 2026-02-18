"""init model """

from odoo import models, fields


class VatMonthlyReportLine(models.Model):
    """
    VAT Tax report monthly line
    """
    _name = "vat.monthly.report.line"
    _description = "VAT Tax Report Grouped Monthly Lines"
    _order = "invoice_type desc, invoice_tax_adjustment desc," \
             " invoice_date, invoice_no"

    monthly_id = fields.Many2one('vat.monthly.report', readonly=True)
    move_id = fields.Many2one('account.move', readonly=True)
    line_id = fields.Many2one('account.move.line', readonly=True)
    product_id = fields.Many2one('product.product', readonly=True)

    document_type = fields.Char(readonly=True)
    tax_type = fields.Char(readonly=True)
    table_product_type = fields.Char(readonly=True)
    invoice_no = fields.Char(readonly=True)
    partner_name = fields.Char(readonly=True)
    registration_number = fields.Char(readonly=True)
    file_number = fields.Char(readonly=True)
    partner_address = fields.Char(readonly=True)
    national_no = fields.Char(readonly=True)
    partner_mobile = fields.Char(readonly=True)
    invoice_date = fields.Char(readonly=True)
    product_name = fields.Char(readonly=True)
    product_code = fields.Char(readonly=True)
    product_type = fields.Selection([('local', '1'),
                                     ('consu', '3'),
                                     ('service', '4'),
                                     ('adjustment', '5')],
                                    readonly=True)
    product_type_name = fields.Selection([('consu', 'Stock'),
                                          ('local', 'Local'),
                                          ('service', 'Service'),
                                          ('adjustment', 'Adjustment')],
                                         readonly=True)
    product_kind = fields.Char(readonly=True)
    product_uom = fields.Char(readonly=True)
    price_unit = fields.Float(readonly=True, group_operator=None)
    tax_percentage = fields.Float(readonly=True, group_operator=None)
    quantity = fields.Float(readonly=True, group_operator=None)
    price_subtotal = fields.Monetary(readonly=True, group_operator=None)
    tax_amount = fields.Monetary(readonly=True)
    price_total = fields.Monetary(string='Total', readonly=True)
    total_tax_with_sign = fields.Monetary(readonly=True)
    currency_id = fields.Many2one('res.currency', readonly=True)
    year = fields.Integer(readonly=True)
    month = fields.Integer(readonly=True)
    invoice_type = fields.Selection(selection=[
        ('entry', 'Journal Entry'),
        ('out_invoice', 'Customer Invoice'),
        ('out_refund', 'Customer Credit Note'),
        ('in_invoice', 'Vendor Bill'),
        ('in_refund', 'Vendor Credit Note'),
        ('out_receipt', 'Sales Receipt'),
        ('in_receipt', 'Purchase Receipt')], string='Type', readonly=True)
    invoice_type_desc = fields.Selection(selection=[
        ('entry', 'Journal Entry'),
        ('out_invoice', 'Customer Invoice'),
        ('out_refund', 'Customer Credit Note'),
        ('in_invoice', 'Vendor Bill'),
        ('in_refund', 'Vendor Credit Note'),
        ('out_receipt', 'Sales Receipt'),
        ('in_receipt', 'Purchase Receipt')], string='Type', readonly=True)
    invoice_tax_adjustment = fields.Boolean(readonly=True)
    invoice_tax_adjustment_name = fields.Selection(readonly=True, selection=[
        ('invoice', 'Invoice'), ('bill', 'Bill'), ('adjustment', 'Adjustment')])
    invoice_tax_reported = fields.Boolean(readonly=True)
