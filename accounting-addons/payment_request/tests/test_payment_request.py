""" Integration test for Test Payment Request """

from odoo.exceptions import ValidationError
from odoo.tests import Form, tagged, TransactionCase


# pylint: disable=too-many-ancestors
@tagged('post_install', '-at_install')
class TestPaymentRequest(TransactionCase):
    """ Integration test for Payment Request """

    def setUp(self):
        """ Setup testing environment """
        super().setUp()
        user_type_income = self.env.ref(
            'account.data_account_type_direct_costs')
        self.account_income = self.env['account.account'].create({
            'code': 'NC1112', 'name':
            'Sale - Test Account',
            'user_type_id': user_type_income.id
        })
        # Create base account to simulate a chart of account
        user_type_payable = self.env.ref('account.data_account_type_payable')
        self.account_payable = self.env['account.account'].create({
            'code': 'AC11100',
            'name': 'Test Payable Account',
            'user_type_id': user_type_payable.id,
            'reconcile': True
        })
        user_type_receivable = self.env.ref(
            'account.data_account_type_receivable')
        self.account_receivable = self.env['account.account'].create({
            'code': 'AC11111',
            'name': 'Test Receivable Account',
            'user_type_id': user_type_receivable.id,
            'reconcile': True
        })
        # Create a customer
        partner = self.env['res.partner']
        self.partner_customer_usd = partner.create({
            'name': 'Customer from the North',
            'email': 'customer.usd@north.com',
            'property_account_payable_id': self.account_payable.id,
            'property_account_receivable_id': self.account_receivable.id,
            'company_id': self.env.ref('base.main_company').id
        })
        seq = self.env.ref('payment_request.payment_request_sequence')
        seq.number_next_actual = 1
        self.partner = self.env.ref('base.res_partner_3')
        product = self.env.ref('product.product_product_8')
        with Form(self.env['account.move'].with_context(
                **{'default_move_type': 'in_invoice'})) as invoice_form:
            invoice_form.partner_id = self.partner_customer_usd
            invoice_form.currency_id = self.env.company.currency_id
            with invoice_form.invoice_line_ids.new() as invoice_line_form:
                invoice_line_form.product_id = product
                invoice_line_form.account_id = self.account_income
        self.invoice = invoice_form.save()
        self.invoice.action_post()

    def test_payment_request(self):
        """ Test Scenario: payment_request() """
        action = self.invoice.action_create_payment_request()
        self.assertTrue(action)
        payment = self.env['payment.request'].browse(action.get('domain')[0][2])
        payment.name = 'PREQ/00001'
        approved = sum(payment.line_ids.mapped('approved_payment_amount'))
        self.assertEqual(payment.total_due,
                         sum(payment.line_ids.mapped('total_due')) - approved)
        self.assertEqual(payment.total_amount, sum(
            payment.line_ids.mapped('total_payment_request')))
        self.assertEqual(payment.total_approved, approved)
        with self.assertRaises(ValidationError):
            payment.action_submit()
        self.env.company.payment_request_responsible_id = \
            self.env.ref('base.user_admin').id
        payment.action_submit()
        self.assertEqual(payment.state, 'submitted')
        payment.action_approve_all()
        for line in payment.line_ids:
            self.assertEqual(line.state, 'approved')
            self.assertEqual(line.currency_id, payment.currency_id)
