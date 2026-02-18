""" Initialize Crossovered Budget """

from odoo import _, api, fields, models


# pylint: disable=no-member
class CrossoveredBudget(models.Model):
    """
        Inherit Crossovered Budget:
    """
    _inherit = 'crossovered.budget'

    amount_type = fields.Selection(
        [('percentage', 'Percentage'),
         ('amount', 'Amount')],
        default='percentage',
        copy=False
    )
    amount = fields.Float(
        copy=False
    )

    @api.onchange('amount_type', 'amount')
    def _onchange_amount(self):
        """ update_type """
        for line in self.crossovered_budget_line:
            line.new_amount = line.planned_amount + (
                self.amount if self.amount_type == 'amount' else
                line.planned_amount * self.amount / 100)

    def action_update_budget(self):
        """ :return Crossovered Budget action """
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'crossovered.budget',
            'name': _('Budget'),
            'view_mode': 'form',
            'context': {'form_view_initial_mode': 'edit', },
            'res_id': self.id,
            'target': 'new',
            'views': [(self.env.ref(
                'budget_update.update_crossovered_budget_form').id, 'form')],
        }

    # pylint: disable=protected-access
    def action_update(self):
        """ Action Update """
        for budget in self:
            new_budget = budget.copy()
            for line in new_budget.crossovered_budget_line:
                line.planned_amount = line.new_amount
            budget.state = 'cancel'
            new_budget._activity_schedule_with_view(
                'mail.mail_activity_data_todo',
                views_or_xmlid='account_budget.crossovered_budget_view_tree',
                user_id=new_budget.user_id.id,
                summary=_('Confirm updated budget %s') % new_budget.name,
            )
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'crossovered.budget',
                'name': _('Budget'),
                'view_mode': 'form',
                'res_id': new_budget.id,
            }
