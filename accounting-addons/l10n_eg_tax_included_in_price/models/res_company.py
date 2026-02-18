"""inherit res.company to add tax group purchase vat """

from odoo import _, fields, models


class ResCompany(models.Model):
    """
    inherit res.company to add tax group purchase vat
    """
    _inherit = 'res.company'

    tax_group_purchase_vat_id = fields.Many2one(
        'account.tax.group',
    )
    fixed_assets_vat_id = fields.Many2one(
        'account.account',
    )
    cost_of_goods_sold_vat_id = fields.Many2one(
        'account.account',
    )
    expense_invest_vat_id = fields.Many2one(
        'account.account',
    )
    expense_vat_id = fields.Many2one(
        'account.account',
    )

    def create_included_taxes(self):
        """ create included taxes from configuration """
        for record in self:
            record.add_vat_tax(
                record.tax_group_purchase_vat_id,
                record.fixed_assets_vat_id,
                _("10% - (VAT Tax amount Included in "
                  "Fixed Assets account)"), )
            record.add_vat_tax(
                record.tax_group_purchase_vat_id,
                record.expense_vat_id,
                _("10% - (VAT Tax amount Included in Exp.account)"),
            )
            record.add_vat_tax(
                record.tax_group_purchase_vat_id,
                record.expense_invest_vat_id,
                _("10% - (VAT Tax amount Included in Purchase "
                  "of Equipment's account)"),
            )
            record.add_vat_tax(
                record.tax_group_purchase_vat_id,
                record.cost_of_goods_sold_vat_id,
                _("10% - (VAT Tax amount Included in COGS account)")
            )

    def add_vat_tax(self, tax_group_id, account_id, name):
        """ fill vat included price taxes """
        tax = self.env['account.tax'].search([('name', '=', name)])
        if not tax and tax_group_id and account_id:
            self.env['account.tax'].create({
                'name': name,
                'description': name,
                'type_tax_use': 'purchase',
                'amount_type': 'percent',
                'amount': 10,
                'tax_group_id': tax_group_id.id,
                'invoice_repartition_line_ids': [
                    (5, 0, 0), (0, 0, {
                        'factor_percent': 100,
                        'repartition_type': 'base'
                    }),
                    (0, 0, {
                        'factor_percent': 100,
                        'repartition_type': 'tax',
                        'account_id': account_id.id,
                    })],
                'refund_repartition_line_ids': [
                    (5, 0, 0), (0, 0, {
                        'factor_percent': 100,
                        'repartition_type': 'base'
                    }),
                    (0, 0, {
                        'factor_percent': 100,
                        'repartition_type': 'tax',
                        'account_id': account_id.id,
                    })]
            })
