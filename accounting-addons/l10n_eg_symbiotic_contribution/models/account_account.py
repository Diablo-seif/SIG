""" inherit account account """
from odoo import fields, models


class AccountAccount(models.Model):
    """ inherit account to add reverse to symbiotic_contribution accounts """
    _inherit = 'account.account'

    symbiotic_contribution_id = fields.Many2one(
        'res.company',
    )
