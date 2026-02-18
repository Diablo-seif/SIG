""" Inherited Product Template """

from odoo import models, api


class ProductTemplate(models.Model):
    """
    Inherit product.template
    add product type fields
    """
    _inherit = 'product.product'

    @api.depends('taxes_id', 'supplier_taxes_id')
    def _compute_tax_domain(self):
        """ prepare the tax domain values """
        for record in self:
            record.tax_in_domain(record)
            record.tax_out_domain(record)

    # pylint: disable=no-member
    @api.onchange('taxes_id')
    def _onchange_taxes_id(self):
        """ update domain table type out """
        self.tax_out_domain(self)
        self.validate_tax_out_types(self)

    # pylint: disable=no-member
    @api.onchange('supplier_taxes_id')
    def _onchange_supplier_taxes_id(self):
        """ update domain table type in """
        self.tax_in_domain(self)
        self.validate_tax_in_types(self)

    @staticmethod
    def tax_in_domain(record):
        """ update tax domain """
        record.account_vat_tax_types_in_domain_table = ""
        record.account_vat_tax_types_in_domain_vat = ""
        for tax in record.supplier_taxes_id:
            if tax.tax_group_id.tax_group_type == 'table':
                record.account_vat_tax_types_in_domain_table = \
                    tax.tax_group_id.table_tax_type
            if tax.tax_group_id.tax_group_type == 'vat':
                record.account_vat_tax_types_in_domain_vat = \
                    tax.tax_group_id.tax_group_type

    @staticmethod
    def tax_out_domain(record):
        """ update tax out domain """
        record.account_vat_tax_types_out_domain_table = ""
        record.account_vat_tax_types_out_domain_vat = ""
        for tax in record.taxes_id:
            if tax.tax_group_id.tax_group_type == 'table':
                record.account_vat_tax_types_out_domain_table = \
                    tax.tax_group_id.table_tax_type
            if tax.tax_group_id.tax_group_type == 'vat':
                record.account_vat_tax_types_out_domain_vat = \
                    tax.tax_group_id.tax_group_type

    @staticmethod
    def validate_tax_in_types(record):
        """ validate tax in type """
        ids = record.account_vat_tax_types_in_ids
        ids_list = record.account_vat_tax_types_in_ids.ids
        for tex_type in ids:
            if tex_type.tax_type != \
                    record.account_vat_tax_types_in_domain_vat and \
                    tex_type.tax_type != \
                    record.account_vat_tax_types_in_domain_table:
                ids_list.remove(tex_type.id.origin)
                record.account_vat_tax_types_in_ids = [(6, 0, ids_list)]

    @staticmethod
    def validate_tax_out_types(record):
        """ validate tax out type """
        ids = record.account_vat_tax_types_out_ids
        ids_list = record.account_vat_tax_types_out_ids.ids
        for tex_type in ids:
            if tex_type.tax_type != \
                    record.account_vat_tax_types_out_domain_vat and \
                    tex_type.tax_type != \
                    record.account_vat_tax_types_out_domain_table:
                ids_list.remove(tex_type.id.origin)
                record.account_vat_tax_types_out_ids = [(6, 0, ids_list)]
