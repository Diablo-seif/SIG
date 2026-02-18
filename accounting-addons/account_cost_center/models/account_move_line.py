""" init object account.move.line """

from odoo import api, fields, models


# pylint: disable=protected-access
class AccountMoveLine(models.Model):
    """ init object account.move.line """
    _inherit = 'account.move.line'

    @api.model
    def _default_cost_center(self):
        """
        Get Default Cost Center
        """
        return self.env['account.cost.center'].browse(
            self.env.context.get('cost_center_id'))

    cost_center_id = fields.Many2one(
        'account.cost.center', string='Cost Center', index=True,
        default=lambda self: self._default_cost_center())
