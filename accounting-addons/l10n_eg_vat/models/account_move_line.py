"""inherit account move line"""

from odoo import fields, models, api


class AccountMoveLine(models.Model):
    """
    inherit account move line
    to add fields of deduction tax
    """
    _inherit = "account.move.line"

    account_vat_tax_types_ids = fields.Many2many(
        'account.vat.tax.types',
        'account_vat_tax_types_lines',
        'account_move_line_id',
        'account_vat_tax_types_id',
        string="Product type (VAT)"
    )
    account_vat_tax_invoice_domain = fields.Char()
    account_vat_tax_types_domain_vat = fields.Char()
    account_vat_tax_types_domain_table = fields.Char()

    # pylint: disable=no-member
    @api.onchange('tax_ids')
    def _onchange_tax_ids(self):
        """ update table type """
        self.account_vat_tax_invoice_domain = 'in'
        if self.move_id.move_type.find("out_") > -1:
            self.account_vat_tax_invoice_domain = 'out'

        for tax in self.tax_ids:
            if tax.tax_group_id.tax_group_type == 'table':
                self.account_vat_tax_types_domain_table = \
                    tax.tax_group_id.table_tax_type
            if tax.tax_group_id.tax_group_type == 'vat':
                self.account_vat_tax_types_domain_vat = \
                    tax.tax_group_id.tax_group_type

    @api.depends('product_id')
    def _compute_tax_type(self):
        """
        compute deduction tax and deduction tax percent
        """
        for line in self:
            if line.move_id.move_type in ['in_invoice', 'in_refund']:
                line.account_vat_tax_types_ids = \
                    line.product_id.account_vat_tax_types_in_ids
            else:
                line.account_vat_tax_types_ids = \
                    line.product_id.account_vat_tax_types_out_ids

    @api.onchange('product_id')
    def onchange_product_id(self):
        """
        compute deduction tax and deduction tax percent
        """
        for line in self:
            if line.move_id.move_type in ['in_invoice', 'in_refund']:
                line.account_vat_tax_types_ids = \
                    line.product_id.account_vat_tax_types_in_ids
            else:
                line.account_vat_tax_types_ids = \
                    line.product_id.account_vat_tax_types_out_ids
