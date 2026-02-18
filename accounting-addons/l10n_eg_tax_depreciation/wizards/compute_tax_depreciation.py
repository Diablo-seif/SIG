"""init model Compute Tax Depreciation"""

from odoo import models, fields


class ComputeTaxDepreciation(models.TransientModel):
    """
    Compute tax depreciation wizard
    """
    _name = "compute.tax.depreciation"
    _description = "Compute tax depreciation wizard"

    recalculate = fields.Boolean(
        default=True,
    )
    compute_all = fields.Boolean()

    def action_compute(self):
        """  call action_compute action """
        self.env['tax.depreciation.category'].compute_tax_deprecation(
            self.recalculate, self.compute_all
        )
