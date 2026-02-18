""" test account asset tax category """
from odoo import fields
from odoo.tests import tagged, TransactionCase


@tagged('post_install', '-at_install')
# pylint: disable=too-many-ancestors
class TestTaxDepreciationCategory(TransactionCase):
    """ Test Tax Depreciation Category """

    def setUp(self):
        """Setup testing environment."""
        super(TestTaxDepreciationCategory, self).setUp()
        user_type_receivable = self.env.ref(
            'account.data_account_type_receivable')
        self.account_receivable = self.env['account.account'].create({
            'code': 'NC1111',
            'name': 'Test Receivable Account',
            'user_type_id': user_type_receivable.id,
            'reconcile': True
        })
        user_type_income = self.env.ref(
            'account.data_account_type_direct_costs')
        self.account_income = self.env['account.account'].create({
            'code': 'NC1112', 'name':
            'Sale - Test Account',
            'user_type_id': user_type_income.id
        })
        user_type_expense = self.env.ref('account.data_account_type_expenses')
        self.account_expense = self.env['account.account'].create({
            'code': 'NC1113',
            'name': 'HR Expense - Test Purchase Account',
            'user_type_id': user_type_expense.id
        })

    # pylint: disable=no-member,too-many-locals,too-many-ancestors
    def test_00_tax_depreciation_category(self):
        """ Test the tax depreciation computation """
        self.env.context = {**self.env.context, **{'asset_type': 'purchase'}}
        new_category = self.env['tax.depreciation.category'].create({
            'name': 'new category',
            'percentage': 5,
            'tax_depreciation_opening_balance': 5000,
            'tax_depreciation_opening_balance_date': fields.Date.from_string(
                '2018-01-01'),
        })
        tax = self.env.ref('l10n_eg_deferred_tax_data.deferred_taxes_default')
        config = self.env['res.config.settings'].create({})
        liability_account = self.account_receivable
        assets_account = self.account_income
        expense_account = self.account_expense
        config.deferred_tax_percentage_id = tax.id
        config.deferred_tax_liabilities_account_id = liability_account.id
        config.deferred_tax_assets_account_id = assets_account.id
        config.deferred_taxes_account_id = expense_account.id
        config.execute()
        new_category.compute_tax_deprecation(True, True)
        dep = new_category.tax_depreciation_category_asset_computation_ids
        self.assertGreaterEqual(len(dep), 3, 'Tax depreciation not added')
        self.assertEqual(
            dep[0].year, 2018,
            'Tax depreciation year not correct')
        new_category.compute_tax_deprecation(False, True)

        self.assertEqual(
            dep[0].tax_depreciated_amount, 250,
            'Tax depreciation amount not correct')
        self.assertEqual(
            dep[0].remaining_amount, 4750,
            'Tax depreciation remaining amount not correct')
        computations = self.env[
            'tax.depreciation.category.asset.computation'].search([
                ('year', '=', '2019')
            ], limit=1)
        computations.with_context(
            active_ids=computations.ids
        ).action_create_update_journal_entries()
        self.assertTrue(computations)
        moves = self.env['account.move'].search([
            ('tax_depreciation_id', '=', computations.id)
        ])
        self.assertEqual(len(moves), 1)
        computations.with_context(
            active_ids=computations.ids
        ).action_create_update_journal_entries()
        moves = self.env['account.move'].search([
            ('tax_depreciation_id', '=', computations.id)
        ])
        self.assertEqual(len(moves), 1)
        moves[0].sudo().action_post()
        computations.with_context(
            active_ids=computations.ids
        ).action_create_update_journal_entries()
        moves = self.env['account.move'].search([
            ('tax_depreciation_id', '=', computations.id)
        ])
        self.assertEqual(len(moves), 3)
