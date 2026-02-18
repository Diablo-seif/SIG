""" Init Python Models"""

from odoo.tests import common


class TestCopyToMonthly(common.TransactionCase):
    """ test vat tax copy to monthly """

    # pylint: disable=protected-access,too-many-locals
    def test_copy_to_monthly(self):
        """ test vat tax copy to monthly """
        # Test copy vat tax to monthly
        new_category = self.env['account.tax.group'].create({
            'name': 'Purchase - Table Tax',
            'sequence': 4
        })
        account = self.env['account.account'].create({
            'name': 'Stock Input',
            'code': 'StockIn',
            'user_type_id': self.env.ref('account.data_account_'
                                         'type_current_assets').id,
        })
        user_type_payable = self.env.ref('account.data_account_type_payable')
        account_payable = self.env['account.account'].create({
            'code': 'NC111000',
            'name': 'Test Payable Account',
            'user_type_id': user_type_payable.id,
            'reconcile': True
        })

        self.env['account.journal'].create({
            'name': 'Vendor Bills - Test',
            'code': 'V-BILL',
            'type': 'purchase',
            'company_id': self.env.user.company_id.id,
        })

        tax_id = self.env['account.tax'].create(
            {'name': 'Table TAX / 5.00%',
             'description': 'Table TAX / 5.00%',
             'type_tax_use': 'sale',
             'amount': 5,
             'include_base_amount': True,
             'tax_group_id': new_category.id,
             'invoice_repartition_line_ids':
                 [(5, 0, 0), (0, 0, {
                     'factor_percent': 100,
                     'repartition_type': 'base'
                 }),
                  (0, 0, {
                      'factor_percent': 100,
                      'repartition_type': 'tax',
                      'account_id': account.id
                  })],
             'refund_repartition_line_ids':
                 [(5, 0, 0), (0, 0, {
                     'factor_percent': 100,
                     'repartition_type': 'base'
                 }),
                  (0, 0, {
                      'factor_percent': 100,
                      'repartition_type': 'tax',
                      'account_id': account.id
                  })]})
        partner_a = self.env.ref('base.res_partner_12')
        product_a = self.env.ref('product.product_product_9')
        vals = {
            'move_type': 'in_invoice',
            'partner_id': partner_a.id,
            'invoice_line_ids': [
                (0, 0, {
                    'product_id': product_a.id,
                    'quantity': 4,
                    'price_unit': 50,
                    'tax_ids': [(6, 0, tax_id.ids)],
                    'account_id': account_payable.id
                })
            ]
        }
        move = self.env['account.move'].create(vals)
        move.action_post()
        ctx = dict(self.env.context)
        _ids = self.env['vat.sales.report.grouped'].search([]).ids
        ctx.update({'active_ids': _ids,
                    'report_model': 'vat.sales.report.grouped'})
        vat_close_report = self.env['vat.close.report']
        vat_close_report_id = vat_close_report.create({
            'close_month': '2',
            'close_year': 2020,
            'mark_as_reported': True
        })
        vat_close_report_id.with_context(ctx).action_close_report()
        vat_monthly_report = self.env['vat.monthly.report'].search(
            [('year', '=', '2020')]
        )
        self.assertGreaterEqual(
            len(vat_monthly_report), 1,
            'VAT Tax grouped records not created')
