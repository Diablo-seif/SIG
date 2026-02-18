""" init Test account cost center """
from odoo.tests import common


class TestAccountCostCenter(common.TransactionCase):
    """ init Test account cost center """

    def setUp(self):
        """
        setUp
        """
        super(TestAccountCostCenter, self).setUp()

        acc_rec = self.env.ref('account.data_account_type_receivable')
        acc_exp = self.env.ref('account.data_account_type_expenses')
        self.invoice_account = self.env['account.account'].search([
            ('user_type_id', '=', acc_rec.id)
        ], limit=1).id
        self.invoice_line_account = self.env['account.account'].search([
            ('user_type_id', '=', acc_exp.id)], limit=1).id
        self.invoice1 = self.env['account.move'].create({
            'partner_id': self.env.ref('base.res_partner_2').id,
            'move_type': 'in_invoice'})
        self.invoice1.write({
            'invoice_line_ids': [
                (0, 0, {
                    'product_id': self.env.ref('product.product_product_2').id,
                    'quantity': 1.0, 'price_unit': 100.0,
                    'name': 'product that cost 100',
                    'account_id': self.invoice_line_account})]})
        self.line1 = self.invoice1.invoice_line_ids[:1]

        self.costcenter = self.env['account.cost.center'].create({
            'name': 'Cost Center Test', 'code': 'CC1',
            'company_id': self.env.user.company_id.id})

        self.invoice2 = self.env['account.move'].create({
            'partner_id': self.env.ref('base.res_partner_2').id,
            'move_type': 'in_invoice',
            'cost_center_id': self.costcenter.id})
        self.invoice2.with_context(cost_center_id=self.costcenter.id).write({
            'invoice_line_ids': [
                (0, 0, {
                    'product_id': self.env.ref('product.product_product_4').id,
                    'quantity': 1.0, 'price_unit': 130.0,
                    'name': 'product that cost 130',
                    'account_id': self.invoice_line_account})]})
        self.line2 = self.invoice2.invoice_line_ids[:1]

    def test_01_check_lines(self):
        """
        Test scenario: check lines.
        """
        self.assertFalse(
            self.line1.cost_center_id, "Default cost center per line not set")

        self.assertTrue(
            (self.line2.cost_center_id == self.costcenter),
            "Default cost center per line set")
