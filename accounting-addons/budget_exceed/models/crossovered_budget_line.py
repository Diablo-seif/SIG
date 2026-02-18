""" Initialize Crossovered Budget Line """

from odoo import _, api, fields, models


# pylint: disable=no-member,protected-access
class CrossoveredBudgetLines(models.Model):
    """
        Inherit Crossovered Budget Line:
    """
    _inherit = 'crossovered.budget.lines'

    over_budget = fields.Monetary()

    @api.model
    def _check_over_budget(self):
        """ Compute over_budget value """
        budget_lines = self.search(
            [('crossovered_budget_id.state', '=', 'done')])
        for line in budget_lines:
            over_budget = abs(line.practical_amount) - abs(line.planned_amount)
            if over_budget > 0 and over_budget != line.over_budget:
                line.crossovered_budget_id._activity_schedule_with_view(
                    'mail.mail_activity_data_todo',
                    views_or_xmlid='account_budget.'
                                   'crossovered_budget_view_tree',
                    user_id=line.crossovered_budget_id.user_id.id,
                    summary=_('%s budget exceeded by %s') %
                    (line.name, over_budget),
                )
                line.over_budget = over_budget
