""" inherit account.tax.template"""
from odoo import fields, models


class AccountTaxTemplate(models.Model):
    """
    inherit account.tax.template to translate name field
    and add deduction code for deduction report integration
    """
    _inherit = 'account.tax.template'

    name = fields.Char(translate=True)
    deduction_code = fields.Char()
    type_tax_deduction = fields.Selection(
        selection=[('withholding', 'Withholding'),
                   ('deduction', 'Deduction'), ],
        string='Tax Type',
    )
    tax_type = fields.Selection(
        selection=[('tax', 'Tax'),
                   ('tax_withholding', 'Deduction/Withholding Tax')],
        default="tax",
    )

    def _get_tax_vals(self, company, tax_template_to_tax):
        """
        override _get_tax_vals to update vals
        to add deduction_code of taxes
        """
        # pylint: disable=no-member
        val = super()._get_tax_vals(company, tax_template_to_tax)
        val.update({
            'deduction_code': self.deduction_code,
            'type_tax_deduction': self.type_tax_deduction,
            'tax_type': self.tax_type,
        })
        return val
