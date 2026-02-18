""" init object account.move """
from odoo import fields, models


class AccountInvoice(models.Model):
    """ init object account.move """
    _inherit = 'account.move'

    cost_center_id = fields.Many2one(
        'account.cost.center', string='Cost Center', readonly=True,
        states={'draft': [('readonly', False)]}, help='Default Cost Center')
