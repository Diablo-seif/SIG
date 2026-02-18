"""Taxes allowances Test Cases"""

from odoo.tests import tagged, TransactionCase


# pylint: disable=protected-access,too-many-ancestors
# pylint: disable=no-member,too-many-instance-attributes
@tagged('post_install', '-at_install')
class DeductionTaxTest(TransactionCase):
    """Deduction Taxes Test Cases"""

    def setUp(self):
        """Setup testing environment."""
        super(DeductionTaxTest, self).setUp()
        self.demo_user = self.env.ref('base.user_demo')
        user_type_payable = self.env.ref('account.data_account_type_payable')
        self.account_payable = self.env['account.account'].create({
            'code': 'NC1110000',
            'name': 'Test Payable Account',
            'user_type_id': user_type_payable.id,
            'reconcile': True
        })
        expenses_type = self.env.ref('account.data_account_type_expenses')
        self.account_expense = self.env['account.account'].create({
            'code': 'NC1113000',
            'name': 'HR Expense - Test Purchase Account',
            'user_type_id': expenses_type.id
        })

        user_type_receivable = self.env.ref(
            'account.data_account_type_receivable')
        self.account_receivable = self.env['account.account'].create({
            'code': 'NC1111000',
            'name': 'Test Receivable Account',
            'user_type_id': user_type_receivable.id,
            'reconcile': True
        })

        self.demo_user.write({
            'groups_id': [(4, self.env.ref('base.group_multi_currency').id)],
        })
        tax_line_vals = [
            (5, 0, 0),
            (0, 0, {
                'factor_percent': 100,
                'repartition_type': 'base',
            }),
            (0, 0, {
                'factor_percent': 100,
                'repartition_type': 'tax',
                'account_id': self.account_receivable.id,
            }),
        ]
        deduction_supply = self.env['account.tax'].create({
            'name': 'Supply Deduction TAX 1.00%',
            'description': 'Supply Deduction TAX 1.00%',
            'amount': -1,
            'type_tax_use': 'purchase',
            'invoice_repartition_line_ids': tax_line_vals,
        })
        deduction_service = self.env['account.tax'].create({
            'name': 'Service Deduction TAX 3.00%',
            'description': 'Service Deduction TAX 3.00%',
            'amount': -3,
            'type_tax_use': 'purchase',
            'invoice_repartition_line_ids': tax_line_vals,
        })
        withholding_supply = self.env['account.tax'].create({
            'name': 'Supply Withholding TAX 1.00%',
            'description': 'Supply Withholding TAX 1.00%',
            'amount': -1,
            'type_tax_use': 'sale',
            'invoice_repartition_line_ids': tax_line_vals,
        })
        withholding_service = self.env['account.tax'].create({
            'name': 'Service Withholding TAX 3.00%',
            'description': 'Service Withholding TAX 3.00%',
            'amount': -3,
            'type_tax_use': 'sale',
            'invoice_repartition_line_ids': tax_line_vals,
        })
        self.product1 = self.env.ref('product.product_product_9')
        self.product1.deduction_tax_id = deduction_supply
        self.product1.withholding_tax_id = withholding_supply
        self.product2 = self.env.ref('product.product_product_10')
        self.product2.deduction_tax_id = deduction_supply
        self.product2.withholding_tax_id = withholding_supply
        self.product3 = self.env.ref('product.product_product_1')
        self.product3.deduction_tax_id = deduction_service
        self.product3.withholding_tax_id = withholding_service
        self.partner1 = self.env.ref('base.res_partner_12')
        self.partner1.write({
            'property_account_payable_id': self.account_payable.id,
            'property_account_receivable_id': self.account_receivable.id,
        })
        account_type_liabilities = self.env.ref(
            'account.data_account_type_current_liabilities'
        )
        account_liability = self.env['account.account'].search(
            [('user_type_id', '=', account_type_liabilities.id)], limit=1
        )
        self.journal = self.env['account.journal'].create({
            'name': 'Deduction Journal',
            'code': '2587',
            'type': 'cash',
            'tax_type': 'deduction',
            'taxation': True,
            'default_account_id': account_liability.id,
        })
        self.journal2 = self.env['account.journal'].create({
            'name': 'Withholding Journal',
            'code': '2588',
            'type': 'cash',
            'tax_type': 'withholding',
            'taxation': True,
        })

    # pylint: disable=no-self-use
    def update_deduction_tax(self, move):
        """
        update_deduction_tax
        """
        for line in move.invoice_line_ids:
            line.deduction_tax_id = line._get_deduction_tax()

    # pylint: disable=too-many-locals
    def test_01_deduction_tax_vendor(self):
        """
        Test Scenario: create bill with products has deduction tax
        to generate deduction tax lines
        then test tax amount in company currency
        """
        account_move = self.env['account.move'].with_user(self.demo_user)
        account_move_line = self.env['account.move.line'].with_user(
            self.demo_user)

        vals = {
            'move_type': 'in_invoice',
            'partner_id': self.partner1.id,
            'invoice_line_ids': [
                (0, 0,
                 {
                     'product_id': self.product1.id,
                     'quantity': 4,
                     'price_unit': 50,
                     'account_id': self.account_expense.id,
                 }),
                (0, 0,
                 {
                     'product_id': self.product2.id,
                     'quantity': 2,
                     'account_id': self.account_expense.id,
                     'price_unit': 100,
                 })
            ]}
        move1 = account_move.create(vals)
        self.update_deduction_tax(move1)
        self.assertEqual(
            len(move1.deduction_tax_line_ids),
            1, 'vendor deduction line (1) not created successfully'
        )
        line2 = account_move_line.new({
            'product_id': self.product3.id,
            'quantity': 2,
            'price_unit': 60,
            'account_id': self.account_expense.id,
        })
        move1.invoice_line_ids = [(4, line2.id)]
        self.update_deduction_tax(move1)
        self.assertEqual(
            len(move1.deduction_tax_line_ids),
            2, 'vendor deduction lines (2) not created successfully'
        )
        # test tax amount in company currency
        tax_amount = move1.deduction_tax_line_ids[0].tax_amount

        # change currency to check total of cost is correct
        old_currency = move1.currency_id
        usd = self.env.ref('base.USD')
        egp = self.env.ref('base.EGP')
        move1.currency_id = usd if usd != old_currency else egp
        # pylint: disable=protected-access
        amount_currency = move1.currency_id._convert(
            tax_amount, old_currency,
            move1.company_id,
            move1.date
        )
        self.assertAlmostEqual(
            move1.deduction_tax_line_ids[0].tax_amount_in_company_currency,
            amount_currency,
            msg='test tax amount in company currency is '
                'not properly calculated.'
        )
        move1.action_post()
        res = move1.action_invoice_register_deduct()
        self.assertIn('default_tax_type', res['context'])
        self.assertIn('default_deduction_payment_type', res['context'])
        self.assertIn('default_taxation_amount', res['context'])
        payment_register = self.env['deduction.register.payment.wizard']. \
            with_context(res['context']).create({
                'payment_method_id': self.env.ref(
                    'account.account_payment_method_manual_out').id,
                'journal_id': self.journal.id})
        self.assertEqual(
            payment_register.total_taxation_amount,
            move1.deduction_tax_total_amount,
            'Total tax amount not set successfully ',
        )
        self.assertTrue(payment_register.hide_payment_method,
                        'payment method should be hidden')
        payment_register._onchange_taxation_percent()
        expected_amount = move1.deduction_tax_residual_amount
        self.assertEqual(
            payment_register.taxation_amount,
            move1.deduction_tax_residual_amount,
            'taxation amount in payment should be equal '
            'residual deduction amount of invoice'
        )
        payment_register.create_payment()
        self.assertEqual(payment_register.taxation_amount, expected_amount)
        res = move1.action_view_payments()
        self.assertIn(
            'res_id', res,
            "res_id is not set successfully"
        )

    def test_02_deduction_tax_customer(self):
        """
        Test Scenario: create invoice with products has deduction tax
        to generate deduction tax lines
        """
        account_move = self.env['account.move']
        vals = {
            'move_type': 'out_invoice',
            'partner_id': self.partner1.id,
            'invoice_line_ids': [
                (0, 0,
                 {
                     'product_id': self.product1.id,
                     'account_id': self.account_expense.id,
                     'quantity': 3,
                     'price_unit': 40,
                 }),
                (0, 0, {
                    'product_id': self.product2.id,
                    'account_id': self.account_expense.id,
                    'quantity': 4,
                    'price_unit': 80,
                }),
                (0, 0, {
                    'product_id': self.product3.id,
                    'account_id': self.account_expense.id,
                    'quantity': 2,
                    'price_unit': 60,
                }),
            ]
        }
        move1 = account_move.create(vals)
        self.update_deduction_tax(move1)
        self.assertEqual(
            len(move1.deduction_tax_line_ids),
            2, 'customer deduction lines (2) not created successfully'
        )
        move1.action_post()
        res = move1.action_invoice_register_deduct()
        payment_register = self.env['deduction.register.payment.wizard']. \
            with_context(res['context']).create({
                'payment_method_id': self.env.ref(
                    'account.account_payment_method_manual_in').id,
                'journal_id': self.journal2.id})
        payment_register.journal_id = self.journal2.id
        # pylint: disable=protected-access
        payment_register._onchange_taxation_percent()
        payment_register.create_payment()
        res = move1.action_view_payments()
        self.assertIn(
            'res_id', res,
            "res_id is not set successfully"
        )

    # pylint: disable=too-many-locals
    def test_03_deduction_tax_vendor_one(self):
        """
        Test Scenario: create bill with products has deduction tax
        to generate deduction tax lines
        then test tax amount in company currency
        from bills list view
        """
        account_move = self.env['account.move'].with_user(self.demo_user)
        account_move_line = self.env['account.move.line'].with_user(
            self.demo_user)

        vals = {
            'move_type': 'in_invoice',
            'partner_id': self.partner1.id,
            'invoice_line_ids': [
                (0, 0,
                 {
                     'product_id': self.product1.id,
                     'quantity': 4,
                     'account_id': self.account_expense.id,
                     'price_unit': 50,
                 },
                 {
                     'product_id': self.product2.id,
                     'account_id': self.account_expense.id,
                     'quantity': 2,
                     'price_unit': 100,
                 },
                 )
            ]
        }
        move1 = account_move.create(vals)
        self.update_deduction_tax(move1)
        self.assertEqual(
            len(move1.deduction_tax_line_ids),
            1, 'vendor deduction line (1) not created successfully'
        )
        line2 = account_move_line.new({
            'product_id': self.product3.id,
            'quantity': 2,
            'account_id': self.account_expense.id,
            'price_unit': 60,
        })
        move1.invoice_line_ids = [(4, line2.id)]
        self.update_deduction_tax(move1)
        self.assertEqual(
            len(move1.deduction_tax_line_ids),
            2, 'vendor deduction lines (2) not created successfully'
        )
        # test tax amount in company currency
        tax_amount = move1.deduction_tax_line_ids[0].tax_amount

        # change currency to check total of cost is correct
        old_currency = move1.currency_id
        usd = self.env.ref('base.USD')
        egp = self.env.ref('base.EGP')
        move1.currency_id = usd if usd != old_currency else egp
        # pylint: disable=protected-access
        amount_currency = move1.currency_id._convert(
            tax_amount, old_currency,
            move1.company_id,
            move1.date
        )
        self.assertAlmostEqual(
            move1.deduction_tax_line_ids[0].tax_amount_in_company_currency,
            amount_currency,
            msg='test tax amount in company currency is '
                'not properly calculated.'
        )
        move1.action_post()
        ctx = dict(self.env.context)
        ctx.update({'active_ids': [move1.id]})
        res = move1.action_invoice_register_deduct()
        self.assertIn('default_tax_type', res['context'])
        self.assertIn('default_deduction_payment_type', res['context'])
        self.assertIn('default_taxation_amount', res['context'])
        payment_register = self.env['deduction.register.payment.wizard'] \
            .with_context(res['context']).create({
                'payment_method_id': self.env.ref(
                    'account.account_payment_method_manual_out').id,
                'journal_id': self.journal.id, })

        self.assertEqual(
            payment_register.total_taxation_amount,
            move1.deduction_tax_total_amount,
            'Total tax amount not set successfully ',
        )
        self.assertTrue(payment_register.hide_payment_method,
                        'payment method should be hidden')
        payment_register._onchange_taxation_percent()
        expected_amount = move1.deduction_tax_residual_amount
        self.assertEqual(
            payment_register.taxation_amount,
            move1.deduction_tax_residual_amount,
            'taxation amount in payment should be equal '
            'residual deduction amount of invoice'
        )
        payment_register.create_payment()
        self.assertEqual(payment_register.taxation_amount, expected_amount)

    # pylint: disable=too-many-locals
    def test_04_deduction_tax_vendor_bulk(self):
        """
        Test Scenario: create 2 bills with products has deduction tax
        to generate deduction tax lines
        then test tax amount in company currency
        from bills list view
        """
        account_move = self.env['account.move'].with_user(self.demo_user)
        account_move_line = self.env['account.move.line'].with_user(
            self.demo_user)

        vals = {
            'move_type': 'in_invoice',
            'partner_id': self.partner1.id,
            'invoice_line_ids': [
                (0, 0,
                 {
                     'product_id': self.product1.id,
                     'quantity': 4,
                     'account_id': self.account_expense.id,
                     'price_unit': 50,
                 },
                 {
                     'product_id': self.product2.id,
                     'quantity': 2,
                     'account_id': self.account_expense.id,
                     'price_unit': 100,
                 },
                 )
            ]
        }
        move1 = account_move.create(vals)
        self.update_deduction_tax(move1)
        self.assertEqual(
            len(move1.deduction_tax_line_ids),
            1, 'vendor deduction line (1) not created successfully'
        )
        line2 = account_move_line.new({
            'product_id': self.product3.id,
            'quantity': 2,
            'account_id': self.account_expense.id,
            'price_unit': 60,
        })
        move1.invoice_line_ids = [(4, line2.id)]
        self.update_deduction_tax(move1)
        self.assertEqual(
            len(move1.deduction_tax_line_ids),
            2, 'vendor deduction lines (2) not created successfully'
        )
        # test tax amount in company currency
        tax_amount = move1.deduction_tax_line_ids[0].tax_amount

        # change currency to check total of cost is correct
        old_currency = move1.currency_id
        usd = self.env.ref('base.USD')
        egp = self.env.ref('base.EGP')
        move1.currency_id = usd if usd != old_currency else egp
        # pylint: disable=protected-access
        amount_currency = move1.currency_id._convert(
            tax_amount, old_currency,
            move1.company_id,
            move1.date
        )
        self.assertAlmostEqual(
            move1.deduction_tax_line_ids[0].tax_amount_in_company_currency,
            amount_currency,
            msg='test tax amount in company currency is '
                'not properly calculated.'
        )
        move1.action_post()

        vals = {
            'move_type': 'in_invoice',
            'partner_id': self.partner1.id,
            'invoice_line_ids': [
                (0, 0,
                 {
                     'product_id': self.product1.id,
                     'quantity': 4,
                     'price_unit': 50,
                     'account_id': self.account_expense.id,
                 },
                 {
                     'product_id': self.product2.id,
                     'account_id': self.account_expense.id,
                     'quantity': 2,
                     'price_unit': 100,
                 },
                 )
            ]
        }
        move2 = account_move.create(vals)
        self.update_deduction_tax(move2)
        self.assertEqual(
            len(move2.deduction_tax_line_ids),
            1, 'vendor deduction line (1) not created successfully'
        )
        line2 = account_move_line.new({
            'product_id': self.product3.id,
            'quantity': 2,
            'account_id': self.account_expense.id,
            'price_unit': 60,
        })
        move2.invoice_line_ids = [(4, line2.id)]
        self.update_deduction_tax(move2)
        self.assertEqual(
            len(move2.deduction_tax_line_ids),
            2, 'vendor deduction lines (2) not created successfully'
        )
        # test tax amount in company currency
        tax_amount = move2.deduction_tax_line_ids[0].tax_amount

        # change currency to check total of cost is correct
        old_currency = move2.currency_id
        usd = self.env.ref('base.USD')
        egp = self.env.ref('base.EGP')
        move2.currency_id = usd if usd != old_currency else egp
        # pylint: disable=protected-access
        amount_currency = move2.currency_id._convert(
            tax_amount, old_currency,
            move2.company_id,
            move2.date
        )
        self.assertAlmostEqual(
            move2.deduction_tax_line_ids[0].tax_amount_in_company_currency,
            amount_currency,
            msg='test tax amount in company currency is '
                'not properly calculated.'
        )
        move2.action_post()

        ctx = dict(self.env.context)
        ctx.update({'active_ids': [move1.id, move2.id]})
        res = move1.action_invoice_register_deduct()
        self.assertIn('default_tax_type', res['context'])
        self.assertIn('default_deduction_payment_type', res['context'])
        payment_register = self.env['deduction.register.payment.wizard']. \
            with_context(res['context']).create({
                'payment_method_id': self.env.ref(
                    'account.account_payment_method_manual_out').id,
                'journal_id': self.journal.id, })

        self.assertEqual(
            payment_register.total_taxation_amount,
            move1.deduction_tax_total_amount,
            'Total tax amount not set successfully ',
        )
        self.assertTrue(payment_register.hide_payment_method,
                        'payment method should be hidden')
        payment_register._onchange_taxation_percent()
        expected_amount = move1.deduction_tax_residual_amount
        self.assertEqual(
            payment_register.taxation_amount,
            move1.deduction_tax_residual_amount,
            'taxation amount in payment should be equal '
            'residual deduction amount of invoice'
        )
        payment_register.create_payment()
        self.assertEqual(payment_register.taxation_amount, expected_amount)
