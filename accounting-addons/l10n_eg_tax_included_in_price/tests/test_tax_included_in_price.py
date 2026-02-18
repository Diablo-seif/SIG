""" test tax included in price"""

from odoo.tests import tagged, TransactionCase


@tagged('post_install', '-at_install')
# pylint: disable=too-many-ancestors
class TestTaxIncludedPrice(TransactionCase):
    """ Test tax included in price """

    def setUp(self):
        """Setup testing environment."""
        super(TestTaxIncludedPrice, self).setUp()
        user_type_expense = self.env.ref('account.data_account_type_expenses')
        self.tax_group = self.env.ref("account.tax_group_taxes")
        self.account_expense = self.env['account.account'].create({
            'code': 'NC1113',
            'name': 'HR Expense - Test Purchase Account',
            'user_type_id': user_type_expense.id
        })

    def test_01_included_price(self):
        """ test create taxes """
        self.env['res.config.settings'].create({
            'tax_group_purchase_vat_id': self.tax_group.id,
            'expense_vat_id': self.account_expense.id,
        }).execute()
        taxes = self.env['account.tax'].search(
            [('name', 'ilike', 'VAT Tax amount Included')])
        self.assertTrue(taxes)
