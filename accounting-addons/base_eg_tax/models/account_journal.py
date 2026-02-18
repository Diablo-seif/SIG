""" Inherited account journal """

from odoo import models, fields


class AccountJournal(models.Model):
    """
    Inherit account.journal
    add field 'Taxation' to can configure taxation
    and separate this journal from other cash journals
    """
    _inherit = 'account.journal'

    taxation = fields.Boolean(default=False)
    tax_type = fields.Selection([
        ('deduction', 'Deduction'),
        ('withholding', 'Withholding'),
    ])
