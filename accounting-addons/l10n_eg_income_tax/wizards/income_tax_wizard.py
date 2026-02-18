"""init income tax calculation wizard"""

import math

from odoo import _, api, fields, models
from odoo.exceptions import UserError


# pylint: disable=protected-access,too-many-function-args
# pylint: disable=no-self-use,too-many-arguments
class IncomeTaxWizard(models.TransientModel):
    """
    income tax wizard calculation
    """
    _name = "income.tax.wizard"
    _description = "income tax calculation wizard"

    revenue_accounts = fields.Many2many(
        'account.account', 'account_income_tax_revenue_rel',
    )
    cogs_accounts = fields.Many2many(
        'account.account', 'account_income_tax_cogs_rel',
    )
    expenses_accounts = fields.Many2many(
        'account.account', 'account_income_tax_expenses_rel',
    )
    depreciation_accounts = fields.Many2many(
        'account.account', 'account_income_tax_depreciation_rel',
    )
    year = fields.Integer(required=True)
    above_seven = fields.Monetary(string="above 7%")
    deferred_losses = fields.Monetary()
    revenue_balance = fields.Monetary(readonly=True)
    cogs_balance = fields.Monetary(readonly=True)
    expenses_balance = fields.Monetary(readonly=True)
    dep_balance = fields.Monetary(readonly=True, string="Depreciation Balance")
    symbiotic_balance = fields.Monetary(string="Symbiotic Contribution")
    net_profit = fields.Monetary(readonly=True)
    tax_depreciation = fields.Monetary()
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='company_id.currency_id'
    )
    partner_id = fields.Many2one(
        'res.partner'
    )

    def calculate_income_tax(self):
        """
        Calculate income tax
        :return:
        """
        if not 1900 < self.year < 9999:
            raise UserError(_("Please enter a correct year"))
        action = self.env.ref(
            'l10n_eg_income_tax.view_income_tax_line_action'
        ).sudo().read()[0]
        action['context'] = dict(self._context, create=False)
        action['domain'] = [('year', '=', self.year)]
        self._calculate_net_profit()
        tax_base = self.net_profit + self.dep_balance + self.above_seven
        base = tax_base - self.tax_depreciation
        base_after_losses = base - self.deferred_losses
        income_lines = self.env['income.tax.line']
        lines = income_lines.search([
            ('year', '=', self.year), ('company_id', '=', self.company_id.id)
        ])
        percentage = self.company_id.deferred_tax_percentage_id.percentage
        entry_lines = []
        if lines:
            entry_lines = self.env['account.move'].search(
                [('income_tax_line_id', 'in', lines.ids)], order='id')
            lines.unlink()
        base_after_losses = self.round_amount(
            base_after_losses,
            self.env.user.company_id.base_after_losses_rounding,
            self.env.user.company_id.base_after_losses_rounding_base,
        )
        amount = base_after_losses * percentage / 100
        amount = self.round_amount(
            amount,
            self.env.user.company_id.income_tax_rounding,
            self.env.user.company_id.income_tax_rounding_base
        )
        income_line_id = income_lines.create({
            'year': self.year,
            'net_profit': self.net_profit,
            'accounting_depreciation': self.dep_balance,
            'above_seven': self.above_seven,
            'tax_base': tax_base,
            'tax_depreciation': self.tax_depreciation,
            'base': base,
            'deferred_losses': self.deferred_losses,
            'base_after_losses': base_after_losses,
            'income_tax': amount,
        })
        if entry_lines:
            entry_lines.write({'income_tax_line_id': income_line_id.id})
        self._add_income_tax_entry(self.year, amount, income_line_id)

        return action

    def calculate_net_profit(self):
        """
        calculate net profit
        return action to prevent wizard from closing
        """
        self._calculate_net_profit()
        # pylint: disable=no-member
        return {
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'income.tax.wizard',
            'res_id': self.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def _calculate_tax_depreciation(self):
        """
        helper method to calculate tax_depreciation
        if l10n_eg_depreciation_income installed
        """
        return

    def _calculate_net_profit(self):
        """
        helper function to calculate net profit
        and all other its parameters needed

        """
        self._calculate_tax_depreciation()
        self.revenue_balance = - self._get_accounts_balance(
            self.revenue_accounts
        )
        self.cogs_balance = self._get_accounts_balance(self.cogs_accounts)
        self.expenses_balance = self._get_accounts_balance(
            self.expenses_accounts
        )
        self.dep_balance = self._get_accounts_balance(
            self.depreciation_accounts
        )
        self.net_profit = self.revenue_balance - (
            self.cogs_balance + self.expenses_balance +
            self.dep_balance + self.symbiotic_balance
        )

    def _get_accounts_balance(self, account_ids):
        """
        helper method to get balance of given accounts
        :param account_ids:
        :return: <float> balance : balance calculated as debit - credit
        """
        move_lines = self.env['account.move.line'].search([
            ('account_id', 'in', account_ids.ids),
            ('move_id.state', '=', 'posted'),
        ])
        lines = move_lines.filtered(lambda l: l.date.year == self.year)
        return sum(lines.mapped('balance'))

    def _add_income_tax_entry(self, year, amount, income_line_id):
        """ add income tax entry
        :param year: <integer>,
        :param amount: <float>,
        :param income_line_id: <income.tax.line>,
        """
        from_account_id = self.env.company.income_tax_entry_from_account_id
        if from_account_id:
            move_ids = self.env['account.move'].search(
                [('income_tax_line_id', '=', income_line_id.id)], order='id')
            self.check_journal_entry(year, move_ids)
            self.create_invoice(
                'Income tax of %s in %s' % (self.year, fields.datetime.now()),
                self.partner_id,
                'in_invoice' if amount >= 0 else 'in_refund',
                abs(amount),
                from_account_id
            )
        else:
            raise UserError(_('Please add income tax accounts in settings'))

    @api.model
    def create_invoice(self, name, partner, invoice_type, amount, account):
        """ Create Invoice """
        invoice = self.env['account.move'].new({
            'partner_id': partner.id,
            'move_type': invoice_type,
        })
        invoice._onchange_partner_id()
        invoice_vals = invoice._convert_to_write(invoice._cache)
        invoice = self.env['account.move'].create(invoice_vals)
        invoice_line = self.env['account.move.line'].new({
            'move_id': invoice.id,
            'account_id': account.id,
            'name': name,
            'price_unit': amount
        })
        invoice_line._onchange_price_subtotal()
        invoice.invoice_line_ids = \
            [(0, 0, invoice_line._convert_to_write(invoice_line._cache))]
        return invoice

    @staticmethod
    def round_amount(amount, income_net_rounding, rounding_base):
        """ round amount
        :param amount: <Float>
        :param income_net_rounding: <string>
        :param rounding_base: <Integer>
        :return amount: <Float>
        """
        rounding = 1
        if rounding_base:
            rounding = rounding_base
        if income_net_rounding == 'ceil':
            amount = (math.ceil(amount / rounding) * rounding)
        elif income_net_rounding == 'floor':
            amount = (math.floor(amount / rounding) * rounding)
        return amount

    def check_journal_entry(self, year, move_ids):
        """ get accounting balance for passed year, accounts
        :param year: <integer>
        :param move_ids: <account.move>
        """
        move_ids = move_ids.filtered(lambda r: r.date.year == year)
        if move_ids:
            draft_moves = move_ids.filtered(lambda r: r.state == 'draft')
            # @formatter:off
            posted_move_ids = move_ids.filtered(
                lambda r: r.state == 'posted' and not r.reversed_entry_id
                and not r.reversal_move_id)
            if draft_moves:
                draft_moves.unlink()
            elif posted_move_ids:
                for move in posted_move_ids:
                    new_move = move._reverse_moves([{
                        'income_tax_line_id': move.income_tax_line_id.id,
                        'ref': move.ref + '-reverse',
                    }])
                    new_move.action_post()
