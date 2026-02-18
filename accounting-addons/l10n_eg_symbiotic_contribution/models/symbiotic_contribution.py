"""new model for symbiotic contribution tax"""

from odoo import fields, models, _
from odoo.exceptions import UserError


class SymbioticContribution(models.Model):
    """ new model for symbiotic contribution tax """

    _name = 'symbiotic.contribution'
    _description = "Symbiotic Contribution Tax"
    _order = 'year'
    _rec_name = 'year'

    year = fields.Integer(
        group_operator=None,
    )
    percentage = fields.Float()
    revenue = fields.Monetary()
    symbiotic_contribution_amount = fields.Monetary()
    currency_id = fields.Many2one(
        'res.currency',
        readonly=True
    )
    account_move_id = fields.Many2one(
        'account.move',
    )

    # pylint: disable=too-many-locals
    def action_compute_symbiotic_contribution(self, year):
        """ compute symbiotic contribution
        :param year: <integer>
        """
        if 1900 <= year <= 9999:
            from_account_id, to_account_id, sy_ids = self.get_accounts()
            if from_account_id and to_account_id and sy_ids:
                obj_move = self.env['account.move']
                move_lines = self.env['account.move.line'].search([
                    ('account_id', 'in', sy_ids.ids),
                    ('move_id.state', '=', 'posted'),
                ]).filtered(lambda l: l.date.year == year)
                revenue = sum(move_lines.mapped('balance'))
                percentage = \
                    self.env.user.company_id.symbiotic_contribution_percentage
                amount = percentage * abs(revenue) / 100
                if amount <= 0:
                    raise UserError(_(
                        'Cannot create journal entry with 0 amount'))
                sy_id = self.env['symbiotic.contribution'].search(
                    [('year', '=', year)])
                vals = {
                    'year': year,
                    'revenue': abs(revenue),
                    'percentage': percentage,
                    'symbiotic_contribution_amount': amount,
                    'currency_id': self.env.user.company_id.currency_id.id,
                }
                if sy_id:
                    sy_id.write(vals)
                else:
                    sy_id = self.env['symbiotic.contribution'].create(vals)

                move_ids = obj_move.search([
                    ('symbiotic_contribution_id', '=', sy_id.id)], order='id')
                self.check_journal_entry(year, move_ids)
                date = fields.Date.to_string(fields.Date.today())
                ref = 'symbiotic contribution of ' + str(
                    sy_id.year) + ' in ' + date
                move = {
                    'name': '/',
                    'date': fields.Date.from_string(
                        str(sy_id.year) + '-12-31'),
                    'ref': ref,
                    'symbiotic_contribution_id': sy_id.id,
                    'line_ids': [(0, 0, {
                        'name': '/', 'debit': amount,
                        'account_id': from_account_id.id,
                    }), (0, 0, {
                        'name': '/', 'credit': amount,
                        'account_id': to_account_id.id,
                    })]
                }
                sy_id.account_move_id = obj_move.create(move)
            else:
                raise UserError(_(
                    'Please add symbiotic contribution accounts in settings'))
        else:
            raise UserError(_('Please enter a correct year'))
        return self.action_return_list(year)

    def get_accounts(self):
        """ get accounts from company
        return account_from_id: <account.account>
        return account_to_id: <account.account>
        return symbiotic_account_ids: [<account.account>]
        """
        return self.env.user.company_id.symbiotic_entry_from_account_id,\
            self.env.user.company_id.symbiotic_entry_to_account_id,\
            self.env.user.company_id.symbiotic_account_ids

    def action_return_list(self, year):
        """
        action return list
        :param year: <integer>
        :return: action list of symbiotic contribution
        """
        action = self.env.ref(
            'l10n_eg_symbiotic_contribution.symbiotic_contribution_action'
        ).sudo().read()[0]
        if year:
            action['domain'] = [('year', '=', year)]
            action['view_mode'] = 'list'
        return action

    # pylint: disable=protected-access,no-self-use
    def check_journal_entry(self, year, move_ids):
        """ get accounting balance for passed year, accounts
        :param year: <integer>
        :param move_ids: <account.move>
        """
        move_ids = move_ids.filtered(lambda r: r.date.year == year)
        if move_ids:
            draft_move_ids = move_ids.filtered(lambda r: r.state == 'draft')
            posted_move_ids = move_ids.filtered(
                lambda r: r.state == 'posted' and not r.reversed_entry_id
                and not r.reversal_move_id)
            if draft_move_ids:
                draft_move_ids.unlink()
            elif posted_move_ids:
                for move in posted_move_ids:
                    new_move = move._reverse_moves([{
                        'symbiotic_contribution_id':
                            move.symbiotic_contribution_id.id,
                        'ref': move.ref + '-reverse',
                    }])
                    new_move.action_post()
