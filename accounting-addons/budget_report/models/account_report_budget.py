""" Initialize Account Report Budget """

from odoo import _, api, models


# pylint: disable=unused-argument,no-self-use,no-member
# pylint: disable=inconsistent-return-statements,too-many-locals
class AccountReportBudget(models.AbstractModel):
    """
        Initialize Account Report Budget:
    """
    _name = 'account.report.budget'
    _description = 'Budget Report'
    _inherit = "account.report"

    filter_date = {'mode': 'range', 'filter': 'this_year'}
    filter_all_entries = True
    filter_analytic = True

    @api.model
    def _get_columns_name(self, options):
        """
            Override function _get_columns_name
        """
        return [
            {'name': '', 'style': 'width:40%'},
            {'name': _('Planned Amount'), 'class': 'number'},
            {'name': _('Practical Amount'), 'class': 'number'},
            {'name': _('Theoretical Amount'), 'class': 'number'},
        ]

    @api.model
    def _get_lines(self, options, line_id=None):
        """
            Override function _get_lines
        """
        lines = []
        date_from = options.get('date', {}).get('date_from')
        date_to = options.get('date', {}).get('date_to')
        analytic_accounts = options.get('analytic_accounts', [])
        domain = [
            ('date_from', '>=', date_from),
            ('date_to', '<=', date_to),
        ]
        states = ['posted']
        states += options.get('all_entries') and ['draft'] or []
        if analytic_accounts:
            domain.append(('analytic_account_id', 'in', analytic_accounts))
        budget_lines = self.env['crossovered.budget.lines'].search(domain)
        budgets = budget_lines.mapped('crossovered_budget_id')

        for budget in budgets:
            lines_budget = budget.crossovered_budget_line.filtered(
                lambda r: r.id in budget_lines.ids)
            lines.append({
                'id': 'budget_%s' % budget.id,
                'name': budget.name,
                'level': 1,
                'unfoldable': True,
                'unfolded': line_id == budget.id or False,
                'columns': [
                    {'name': sum(lines_budget.mapped('planned_amount')),
                     'class': 'number'},
                    {'name': lines_budget.get_practical_amount(states),
                     'class': 'number'},
                    {'name': sum(lines_budget.mapped('theoritical_amount')),
                     'class': 'number'},
                ],
            })
            for line in lines_budget:
                lines.append({
                    'id': 'budget_line_%s' % line.id,
                    'name': line.name,
                    'level': 4,
                    'caret_options': 'budget',
                    'parent_id': 'budget_%s' % budget.id,
                    'columns': [
                        {'name': sum(line.mapped('planned_amount')),
                         'class': 'number'},
                        {'name': line.get_practical_amount(states),
                         'class': 'number'},
                        {'name': sum(line.mapped('theoritical_amount')),
                         'class': 'number'}
                    ],
                })
        lines.append({
            'id': 'total_budget',
            'name': 'Total',
            'level': 0,
            'class': 'total',
            'columns': [
                {'name': sum(budget_lines.mapped('planned_amount')),
                 'class': 'number'},
                {'name': budget_lines.get_practical_amount(states),
                 'class': 'number'},
                {'name': sum(budget_lines.mapped('theoritical_amount')),
                 'class': 'number'}
            ],
        })
        return lines

    @api.model
    def _get_report_name(self):
        """
            Overide Function  _get_report_name
        """
        return _("Budget")

    @api.model
    def _get_templates(self):
        """
            Override function _get_templates
        """
        templates = super()._get_templates()
        templates['line_template'] = 'budget_report.line_template_budget_report'
        return templates

    def open_journal_entry(self, options, params=None):
        """ get budget line journal entries """
        line_id = params.get('id').split('_')[-1]
        if line_id:
            return self.env['crossovered.budget.lines'].browse(
                int(line_id)).action_open_budget_entries()

    def view_general_ledger(self, options, params=None):
        """ Open General Ledger """
        if not params:
            params = {}
        ctx = self.env.context.copy()
        ctx.pop('id', '')
        action = self.env.ref(
            'account_reports.action_account_report_general_ledger'
        ).sudo().read()[0]
        ctx.update({'model': 'account.general.ledger'})
        budget_line = self.env['crossovered.budget.lines'].browse(
            int(params.get('id').split('_')[-1]))
        account_ids = budget_line.general_budget_id.mapped(
            'account_ids').ids
        acc_list = ['account_%s' % acc for acc in account_ids]
        options.update({'unfolded_lines': acc_list})
        action.update(
            {'options': options, 'context': ctx, 'ignore_session': 'read'})
        return action
