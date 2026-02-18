""" tax.depreciation.category"""
from odoo import fields, models, _
from odoo.exceptions import UserError


class TaxDepreciationCategoryAssetComputation(models.Model):
    """
    tax.depreciation.category.asset.computation
    """
    _name = 'tax.depreciation.category.asset.computation'
    _description = "Tax Depreciation Category Asset Computation"
    _order = 'year'

    year = fields.Integer(
        group_operator=None,
    )
    currency_id = fields.Many2one(
        'res.currency',
        readonly=True,
    )
    opening_balance = fields.Float()
    disposed_sold = fields.Float()
    purchased = fields.Float()
    percentage = fields.Float()
    amount = fields.Monetary()
    tax_depreciated_amount = fields.Monetary()
    remaining_amount = fields.Monetary()
    accounting_depreciation = fields.Monetary()
    depreciation_difference = fields.Monetary()
    deferred_tax_amount = fields.Monetary()
    tax_depreciation_category_id = fields.Many2one(
        'tax.depreciation.category',
        string="Category",
    )
    default_entry_line = fields.Boolean()
    account_move_id = fields.Many2one('account.move')

    def action_create_update_journal_entries(self):
        """ action create update journal entries
        """
        active_ids = self.env.context.get('active_ids')
        if active_ids:
            category_ids = self.browse(active_ids)
            if category_ids:
                category_set = set(category_ids.mapped('year'))
                if len(category_set) > 1:
                    raise UserError(_('Please select one year only'))
                else:
                    self.create_update_journal_entries(category_set)

    def create_update_journal_entries(self, category_set):
        """ action create update journal entries
        :param category_set: <tax.depreciation.category.asset.computation>
        """
        year = list(category_set)[0]
        record_ids = self.search([('year', '=', year)])
        deferred_tax_amount = sum(
            record_ids.mapped('deferred_tax_amount'))
        obj_move = self.env['account.move']
        if deferred_tax_amount != 0:
            from_account_id, to_account_id = self.get_accounts(
                deferred_tax_amount)
            if from_account_id and to_account_id:
                # validate default depreciation line exist
                record_id = record_ids.filtered(
                    lambda r: r.default_entry_line)
                if not record_id:
                    record_id = record_ids[0]
                    record_id.default_entry_line = True
                # validate default depreciation entry exist
                move_ids = obj_move.search(
                    [('tax_depreciation_id', '=', record_id.id)],
                    order='id'
                )
                self.check_journal_entry(year, move_ids)
                amount = abs(deferred_tax_amount)
                name = fields.Datetime.to_string(fields.datetime.now())
                move = {
                    'name': '/',
                    'date': fields.Date.from_string(
                        str(record_id.year) + '-12-31'),
                    'ref': 'deferred taxes of' + str(
                        record_id.year) + ' in ' + name,
                    'tax_depreciation_id': record_id.id,
                    'line_ids': [
                        (0, 0, {
                            'name': '/', 'debit': amount,
                            'account_id': from_account_id.id}),
                        (0, 0, {
                            'name': '/', 'credit': amount,
                            'account_id': to_account_id.id})]
                }
                record_id.account_move_id = obj_move.create(move)
            else:
                raise UserError(_(
                    "Please select deferred accounts, in settings"))
        else:
            raise UserError(_("Deferred tax equal 0, can not add entry"))

    def get_accounts(self, sign):
        """ get accounts from company
        :param sign: <integer>
        return account_from_id: <account.account>
        return account_to_id: <account.account>
        """
        from_id = to_id = False
        if sign > 0:
            from_id = self.env.user.company_id.deferred_taxes_account_id
            to_id = self.env.user.company_id.deferred_tax_liabilities_account_id
        elif sign < 0:
            from_id = self.env.user.company_id.deferred_tax_assets_account_id
            to_id = self.env.user.company_id.deferred_taxes_account_id
        return from_id, to_id

    # pylint: disable=protected-access,no-self-use
    def check_journal_entry(self, year, move_ids):
        """ get accounting balance for passed year, accounts
        :param year: <integer>
        :param move_ids: <account.move>
        """
        move_ids = move_ids.filtered(lambda r: r.date.year == year)
        if move_ids:
            draft_move_ids = move_ids.filtered(lambda r: r.state == 'draft')
            posted_move_ids = move_ids.filtered(
                lambda r: r.state == 'posted' and not r.reversed_entry_id
                and not r.reversal_move_id)
            if draft_move_ids:
                draft_move_ids.unlink()
            elif posted_move_ids:
                for move in posted_move_ids:
                    new_move = move._reverse_moves([{
                        'tax_depreciation_id': move.tax_depreciation_id.id,
                        'ref': move.ref + '-reverse',
                    }])
                    new_move.action_post()
