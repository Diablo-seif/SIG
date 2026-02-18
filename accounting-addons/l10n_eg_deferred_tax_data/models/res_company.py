"""inherit res.company to add Deferred Tax Percentage"""

from odoo import fields, models


class ResCompany(models.Model):
    """
    inherit res.company to add Deferred Tax Percentage
    """
    _inherit = 'res.company'

    deferred_tax_percentage_id = fields.Many2one(
        'deferred.tax.percentage',
    )
