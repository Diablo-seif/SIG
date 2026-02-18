"""inherit account move"""
from odoo import fields, models


class AccountMove(models.Model):
    """ inherit account move to add income tax line link"""
    _inherit = 'account.move'

    income_tax_line_id = fields.Many2one('income.tax.line')
