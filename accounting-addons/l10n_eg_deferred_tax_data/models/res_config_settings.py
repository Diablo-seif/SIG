""" inherit res.config.settings to add Deferred Tax Percentage"""

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    """
    inherit res.config.settings to add Deferred Tax Percentage
    """
    _inherit = 'res.config.settings'

    deferred_tax_percentage_id = fields.Many2one(
        'deferred.tax.percentage',
        related='company_id.deferred_tax_percentage_id',
        readonly=False
    )
