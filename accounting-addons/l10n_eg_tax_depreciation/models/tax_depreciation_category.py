""" tax.depreciation.category"""
from odoo import fields, models, api, _
from odoo.exceptions import UserError


class TaxDepreciationCategory(models.Model):
    """
    tax.depreciation.category
    """
    _name = 'tax.depreciation.category'
    _description = "Tax Depreciation Type"
    _order = "name"

    name = fields.Char(
        translate=True,
    )
    percentage = fields.Float()
    tax_depreciation_opening_balance = fields.Float(
        string="Opening Balance",
    )
    tax_depreciation_opening_balance_date = fields.Date(
        string="Opening Balance Date",
    )
    tax_depreciation_category_asset_computation_ids = fields.One2many(
        'tax.depreciation.category.asset.computation',
        'tax_depreciation_category_id',
    )
    account_asset_ids = fields.One2many(
        'account.account',
        'tax_depreciation_category_fixed_id',
        string='Fixed Asset Accounts'
    )
    account_depreciation_ids = fields.One2many(
        'account.account',
        'tax_depreciation_category_depreciation_id',
        string='Depreciation Accounts'
    )

    @api.constrains('percentage')
    def _constraint_percentage(self):
        for record in self:
            if not record.percentage > 0:
                raise UserError(_("Percentage should be greater than 0"))

    def compute_tax_deprecation(self, recompute, compute_all):
        """ compute tax deprecation
        :param recompute: <boolean>
        :param compute_all: <boolean>
        """
        category_ids = []
        active_id = self.env.context.get('active_id', 0)
        if active_id > 0:
            category_ids = self.browse(active_id)
        if compute_all:
            category_ids = self.env['tax.depreciation.category'].search([])
        for category_id in category_ids:
            self.compute_tax_deprecation_category(category_id, recompute)

    def compute_tax_deprecation_category(self, category_id, recompute):
        """ compute tax deprecation
         :param category_id: <tax.depreciation.category>
         :param recompute: <boolean>
         """
        op_balance = category_id.tax_depreciation_opening_balance
        if not category_id.tax_depreciation_opening_balance_date:
            return

        start_year = category_id.tax_depreciation_opening_balance_date.year
        if not recompute:
            dep_ids = self.env['tax.depreciation.category.asset.computation'] \
                .search(
                    [('tax_depreciation_category_id', '=', category_id.id)],
                    order='year desc'
                )
            if dep_ids:
                start_year = dep_ids[0].year
                op_balance = dep_ids[0].remaining_amount

        if start_year > fields.date.today().year:
            return
        for year in range(start_year, fields.date.today().year + 1):
            op_balance = self.compute_tax_deprecation_category_year(
                category_id, year, op_balance)

    # pylint: disable=too-many-locals
    def compute_tax_deprecation_category_year(self, category_id,
                                              year, op_balance):
        """ compute tax deprecation category year
         :param category_id: <tax.depreciation.category>
         :param year: <integer>
         :param op_balance: <integer>
         :return balance: <float>
        """
        purchased_amount = self.get_category_purchased_amount(
            category_id, year
        )
        disposed_sold_amount = self.get_category_disposed_sold_amount(
            category_id, year)
        move_lines = self.env['account.move.line'].search([
            ('account_id', 'in', category_id.account_depreciation_ids.ids),
            ('move_id.state', '=', 'posted'),
        ])
        lines = move_lines.filtered(lambda l: l.date.year == year)
        accounting_depreciation = sum(lines.mapped('balance'))

        dep_object = self.env['tax.depreciation.category.asset.computation']
        dep_id = dep_object.search([('year', '=', year),
                                    ('tax_depreciation_category_id',
                                     '=', category_id.id)])
        amount = op_balance + purchased_amount - disposed_sold_amount
        depreciation = amount * category_id.percentage / 100
        depreciation_difference = depreciation + accounting_depreciation
        prcnt = 0
        if self.env.user.company_id.deferred_tax_percentage_id:
            prcnt = self.env.user.company_id.deferred_tax_percentage_id. \
                percentage
        vals = {
            'currency_id': self.env.user.company_id.currency_id.id,
            'opening_balance': op_balance,
            'disposed_sold': disposed_sold_amount,
            'purchased': purchased_amount,
            'percentage': category_id.percentage,
            'amount': amount,
            'tax_depreciated_amount': depreciation,
            'remaining_amount': amount - depreciation,
            'accounting_depreciation': abs(accounting_depreciation),
            'depreciation_difference': depreciation_difference,
            'deferred_tax_amount': depreciation_difference * prcnt / 100,
            'year': year,
            'tax_depreciation_category_id': category_id.id}

        if dep_id:
            dep_id[0].write(vals)
        else:
            dep_object.create(vals)
        return vals['remaining_amount']

    def get_category_purchased_amount(self, category_id, year):
        """ get category purchased amount from assets for this category
         :param category_id: <tax.depreciation.category>
         :param year: <integer>
         :return purchase amount: <float>
        """
        if not category_id:
            return 0

        move_lines = self.env['account.move.line'].search([
            ('account_id', 'in', category_id.account_asset_ids.ids),
            ('debit', '!=', 0),
            ('move_id.state', '=', 'posted'),
        ])
        lines = move_lines.filtered(lambda l: l.date.year == year)
        return sum(l.debit for l in lines)

    def get_category_disposed_sold_amount(self, category_id, year):
        """ get category disposed/sold amount from assets for this category
         :param category_id: <tax.depreciation.category>
         :param year: <integer>
         :return dispose and sold amount: <float>
        """
        if not category_id:
            return 0

        move_lines = self.env['account.move.line'].search([
            ('account_id', 'in', category_id.account_asset_ids.ids),
            ('credit', '!=', 0),
            ('move_id.state', '=', 'posted'),
        ])
        lines = move_lines.filtered(lambda l: l.date.year == year)
        return sum(l.credit for l in lines)

    def compute_tax_deprecation_wizard(self):
        """  call compute tax deprecation wizard """
        # self.compute_tax_deprecation(False, False)
        view_id = self.env.ref('l10n_eg_tax_depreciation.'
                               'compute_tax_depreciation_view_form').id

        return {
            'name': _('Compute Tax Deprecation'),
            'res_model': 'compute.tax.depreciation',
            'view_mode': 'form',
            'view_id': view_id,
            'context': self.env.context,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }
