"""inherit account move"""
from odoo import fields, models


class AccountMove(models.Model):
    """ inherit account move to add tax category computation link"""
    _inherit = 'account.move'

    tax_depreciation_id = fields.Many2one(
        'tax.depreciation.category.asset.computation',
    )
