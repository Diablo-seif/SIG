""" Initialize Product Template """

from odoo import fields, models


class ProductTemplate(models.Model):
    """
        Inherit Product Template:
    """
    _inherit = 'product.template'

    global_product_classification_type = fields.Selection(
        [('EGS', 'EGS'), ('GS1', 'GS1')], default='GS1')
    global_product_classification = fields.Char()
