""" Initialize Account Move """

from odoo import fields, models


class AccountMove(models.Model):
    """
        Inherit Account Move:
    """
    _inherit = 'account.move'

    insertion_method = fields.Selection(
        [('automatic', 'Automatic'),
         ('manual', 'Manual')],
        default='automatic',
    )
