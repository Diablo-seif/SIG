""" Initialize Crossovered Budget Line """

from odoo import api, fields, models


# pylint: disable=no-member
class CrossoveredBudgetLines(models.Model):
    """
        Inherit Crossovered Budget Line:
    """
    _inherit = 'crossovered.budget.lines'

    new_amount = fields.Monetary()
    difference_amount = fields.Monetary(
        compute='_compute_difference_amount'
    )

    @api.depends('planned_amount', 'new_amount')
    def _compute_difference_amount(self):
        """ Compute difference_amount value """
        for rec in self:
            rec.difference_amount = rec.planned_amount - rec.new_amount

    @api.onchange('planned_amount')
    def _onchange_planned_amount(self):
        """ planned_amount """
        self.new_amount = self.planned_amount
