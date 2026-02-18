"""inherit account move"""
from odoo import fields, models


class AccountMove(models.Model):
    """ inherit account move to add symbiotic contribution link"""
    _inherit = 'account.move'

    symbiotic_contribution_id = fields.Many2one(
        'symbiotic.contribution',
    )
