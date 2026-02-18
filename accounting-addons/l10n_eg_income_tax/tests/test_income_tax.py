"""Income Tax Test Cases"""

from odoo.tests import tagged, TransactionCase


@tagged('post_install', '-at_install')
# pylint: disable=too-many-ancestors,too-many-instance-attributes
class IncomeTaxTest(TransactionCase):
    """Income Taxes Test Cases"""

    def setUp(self):
        """Setup testing environment."""
        super(IncomeTaxTest, self).setUp()
        accounts = self.env['account.account']
        revenue_type = self.env.ref('account.data_account_type_revenue')
        self.account_revenue = self.env['account.account'].create({
            'code': 'NC1114',
            'name': 'Sales - Test Sales Account',
            'user_type_id': revenue_type.id,
            'reconcile': True
        })
        cogs_type = self.env.ref('account.data_account_type_direct_costs')
        self.account_income = self.env['account.account'].create({
            'code': 'NC1112', 'name':
            'Sale - Test Account',
            'user_type_id': cogs_type.id
        })
        expenses_type = self.env.ref('account.data_account_type_expenses')
        self.account_expense = self.env['account.account'].create({
            'code': 'NC1113',
            'name': 'HR Expense - Test Purchase Account',
            'user_type_id': expenses_type.id
        })
        depreciation_type = self.env.ref(
            'account.data_account_type_depreciation'
        )
        self.journal_general = self.env['account.journal'].create({
            'name': 'General Journal - Test',
            'code': 'AJ-GENERAL',
            'type': 'general',
            'company_id': self.env.user.company_id.id,
        })

        tax = self.env.ref('l10n_eg_deferred_tax_data.deferred_taxes_default')
        self.env.company.deferred_tax_percentage_id = tax.id
        self.revenue_accounts = accounts.search(
            [('user_type_id', '=', revenue_type.id)]
        )
        self.cogs_accounts = accounts.search(
            [('user_type_id', '=', cogs_type.id)]
        )
        self.expenses_accounts = accounts.search(
            [('user_type_id', '=', expenses_type.id)]
        )
        self.depreciation_accounts = accounts.search(
            [('user_type_id', '=', depreciation_type.id)]
        )
        user_type_receivable = self.env.ref(
            'account.data_account_type_receivable')
        self.account_receivable = self.env['account.account'].create({
            'code': 'NC1111',
            'name': 'Test Receivable Account',
            'user_type_id': user_type_receivable.id,
            'reconcile': True
        })
        move = self.env['account.move'].create({
            'move_type': 'entry',
            'journal_id': self.journal_general.id,
            'line_ids': [(0, 0, {
                'name': '/', 'debit': 10000,
                'account_id': self.account_receivable.id,
            }), (0, 0, {
                'name': '/', 'credit': 10000,
                'account_id': self.account_revenue.id,
            })]

        })
        move.action_post()

    def test_income_tax(self):
        """
        test net profit and income tax calculations
        check returns of every method
        """
        tax_wizard = self.env['income.tax.wizard'].create({
            'revenue_accounts': self.revenue_accounts,
            'cogs_accounts': self.cogs_accounts,
            'expenses_accounts': self.expenses_accounts,
            'depreciation_accounts': self.depreciation_accounts,
            'year': 2020,
            'above_seven': 5000,
            'deferred_losses': 2000,
            'tax_depreciation': 2500,
        })
        from_account_id = self.account_income
        self.env.user.company_id.income_tax_entry_from_account_id = \
            from_account_id
        res = tax_wizard.calculate_net_profit()
        self.assertIn('res_id', res)
        self.assertEqual(res['res_id'], tax_wizard.id)
        res2 = tax_wizard.calculate_income_tax()
        self.assertIn('res_model', res2)
        self.assertEqual(res2['res_model'], 'income.tax.line')
