""" test symbiotic contribution """

from odoo.tests import tagged, TransactionCase
from odoo import fields


@tagged('post_install', '-at_install')
# pylint: disable=no-member,too-many-locals,too-many-ancestors
class TestSymbioticContribution(TransactionCase):
    """ Test Symbiotic Contribution """

    def setUp(self):
        """Setup testing environment."""
        super(TestSymbioticContribution, self).setUp()
        user_type_payable = self.env.ref('account.data_account_type_payable')
        self.account_payable = self.env['account.account'].create({
            'code': 'NC1110',
            'name': 'Test Payable Account',
            'user_type_id': user_type_payable.id,
            'reconcile': True
        })
        user_type_receivable = self.env.ref(
            'account.data_account_type_receivable')
        self.account_receivable = self.env['account.account'].create({
            'code': 'NC1111',
            'name': 'Test Receivable Account',
            'user_type_id': user_type_receivable.id,
            'reconcile': True
        })
        user_type_revenue = self.env.ref('account.data_account_type_revenue')
        self.account_revenue = self.env['account.account'].create({
            'code': 'NC1114',
            'name': 'Sales - Test Sales Account',
            'user_type_id': user_type_revenue.id,
            'reconcile': True
        })

    def test_00_symbiotic_contribution(self):
        """ Test symbiotic contribution """
        year = fields.Date.today().year
        wiz_id = self.env['symbiotic.contribution.computation'].create(
            {'year': year})
        self.env.user.company_id.symbiotic_contribution_percentage = 2.5
        new_category = self.env['account.tax.group'].create({
            'name': 'Purchase - Table Tax',
            'sequence': 4
        })
        tax_id = self.env['account.tax'].create({
            'name': 'Table TAX - 5.00% -',
            'description': 'Table TAX - 5.00% - ',
            'type_tax_use': 'sale',
            'amount': 5,
            'include_base_amount': True,
            'tax_group_id': new_category.id,
            'invoice_repartition_line_ids': [
                (5, 0, 0), (0, 0, {
                    'factor_percent': 100,
                    'repartition_type': 'base'
                }),
                (0, 0, {
                    'factor_percent': 100,
                    'repartition_type': 'tax',
                    'account_id': self.account_revenue.id
                })],
            'refund_repartition_line_ids': [
                (5, 0, 0), (0, 0, {
                    'factor_percent': 100,
                    'repartition_type': 'base'
                }),
                (0, 0, {
                    'factor_percent': 100,
                    'repartition_type': 'tax',
                    'account_id': self.account_revenue.id
                })]})
        self.env.user.company_id.symbiotic_entry_from_account_id = \
            self.account_revenue.id
        to_account_id = self.account_revenue
        self.env.user.company_id.symbiotic_entry_to_account_id = \
            to_account_id
        self.env.user.company_id.symbiotic_account_ids = \
            [(4, self.account_revenue.id)]

        partner_a = self.env.ref('base.res_partner_12')
        partner_a.write({
            'property_account_payable_id': self.account_payable.id,
            'property_account_receivable_id': self.account_receivable.id,
        })

        product_line1 = self.env.ref('product.product_product_9')
        move_id = self.env['account.move'].create({
            'move_type': 'in_invoice',
            'partner_id': partner_a.id,
            'invoice_date': fields.Date.from_string(str(year) + '-12-31'),
            'invoice_line_ids': [
                (0, 0, {
                    'product_id': product_line1.id,
                    'quantity': 4,
                    'price_unit': 50,
                    'tax_ids': [(6, 0, tax_id.ids)],
                    'account_id': self.account_revenue.id,
                },)]
        })
        move_id.action_post()
        wiz_id.action_compute()
        sy_id = self.env['symbiotic.contribution'].search(
            [('year', '=', year)])
        self.assertGreaterEqual(
            sy_id.symbiotic_contribution_amount, 5.0,
            'Symbiotic contribution entry not created')
