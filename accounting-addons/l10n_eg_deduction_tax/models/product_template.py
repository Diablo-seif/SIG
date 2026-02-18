""" Inherited Product Template """

from odoo import models, fields


class ProductTemplate(models.Model):
    """
    Inherit product.template
    add fields to can configure deduction/withholding taxes on products
    """
    _inherit = 'product.template'

    deduction_tax_id = fields.Many2one(
        'account.tax', domain=[('type_tax_use', '=', 'purchase')])
    withholding_tax_id = fields.Many2one(
        'account.tax', domain=[('type_tax_use', '=', 'sale')])
