"""inherit account tax group"""

from odoo import fields, models


class AccountTaxGroup(models.Model):
    """
    inherit account tax group
    to add fields for tax group type
    """
    _inherit = "account.tax.group"

    tax_group_type = fields.Selection([
        ('vat', 'VAT'),
        ('table', 'Table'),
        ('deduction', 'Deduction'),
        ('withholding', 'Withholding'),
        ('others', 'Others'),
    ])

    table_tax_type = fields.Selection([
        ('table1', 'Table 1'),
        ('table2', 'Table 2'),
        ('others', 'Others'),
    ], default='others')
