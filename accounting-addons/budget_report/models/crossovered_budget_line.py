""" Initialize Crossovered Budget Line """

from odoo import api, models


# pylint: disable=no-member,too-many-locals,protected-access,sql-injection
class CrossoveredBudgetLines(models.Model):
    """
        Inherit Crossovered Budget Line:
    """
    _inherit = 'crossovered.budget.lines'

    @api.model
    def get_practical_amount(self, state):
        """ get_practical_amount """
        total_amount = 0
        for line in self:
            acc_ids = line.general_budget_id.account_ids.ids
            date_to = line.date_to
            date_from = line.date_from
            if line.analytic_account_id.id:
                analytic_line_obj = self.env['account.analytic.line']
                domain = [('account_id', '=', line.analytic_account_id.id),
                          ('date', '>=', date_from),
                          ('date', '<=', date_to),
                          ]
                if acc_ids:
                    domain += [('general_account_id', 'in', acc_ids)]
                where_query = analytic_line_obj._where_calc(domain)
                analytic_line_obj._apply_ir_rules(where_query, 'read')
                from_clause, where_clause, where_clause_params = \
                    where_query.get_sql()
                select = "SELECT SUM(amount) from " + \
                         from_clause + " where " + where_clause
            else:
                aml_obj = self.env['account.move.line']
                domain = [('account_id', 'in',
                           line.general_budget_id.account_ids.ids),
                          ('date', '>=', date_from),
                          ('date', '<=', date_to),
                          ('move_id.state', '=', state)]
                where_query = aml_obj._where_calc(domain)
                aml_obj._apply_ir_rules(where_query, 'read')
                from_clause, where_clause, where_clause_params = \
                    where_query.get_sql()
                select = "SELECT sum(credit)-sum(debit) from " + \
                         from_clause + " where " + where_clause
            self.env.cr.execute(select, where_clause_params)
            total_amount += self.env.cr.fetchone()[0] or 0.0
        return total_amount
