"""init Deferred Tax Percentage model"""

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class DeferredTaxPercentage(models.Model):
    """
    init Deferred Tax Percentage
    """
    _name = 'deferred.tax.percentage'

    name = fields.Char(
        required=True,
        translate=True,
    )
    percentage = fields.Float(
        required=True,
    )

    @api.constrains('percentage')
    def _constraint_percentage(self):
        """
        set constraints on percentage
        to be  :
        100>= percent >= 0
        """
        for record in self:
            if record.percentage < 0:
                raise UserError(_("Percentage should be greater than 0"))
            if record.percentage > 100:
                raise UserError(_("Percentage should be less than 100"))
