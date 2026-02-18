""" Initialize register payment wizard """
from odoo import _, api, fields, models
from odoo.exceptions import UserError


# pylint: disable=protected-access
class DeductionRegisterPaymentWizard(models.TransientModel):
    """ Initialize register payment wizard """

    _name = "deduction.register.payment.wizard"
    _description = "Deduction Register Payment Wizard"

    company_id = fields.Many2one(
        'res.company', default=lambda self: self.env.company)
    journal_id = fields.Many2one(
        'account.journal', required=True,
        domain="[('type', 'in', ['bank', 'cash']), ('taxation', '=', True), "
               "('tax_type', '=', tax_type), ('company_id', '=', company_id)]")
    currency_id = fields.Many2one(
        'res.currency', string='Currency', required=True,
        default=lambda self: self.env.company.currency_id)
    payment_date = fields.Date(default=fields.Date.context_today, required=True)
    ref = fields.Char(string='Memo')
    payment_method_id = fields.Many2one(
        'account.payment.method',
        domain="[('id', 'in', available_payment_method_ids)]",
        readonly=False, store=True, compute='_compute_payment_method_id')
    available_payment_method_ids = fields.Many2many(
        'account.payment.method', compute='_compute_payment_method_fields')
    hide_payment_method = fields.Boolean(
        compute='_compute_payment_method_fields')
    edit_payment = fields.Boolean()

    # taxation fields
    tax_type = fields.Selection([
        ('deduction', 'Deduction'), ('withholding', 'Withholding')])
    taxation_amount = fields.Monetary()
    total_taxation_amount = fields.Monetary()
    residual_taxation_amount = fields.Monetary()
    deduction_payment_type = fields.Selection(
        [('full', 'Full'), ('percentage', 'Percentage'), ('amount', 'Amount')])
    taxation_percent = fields.Float()
    deduction_type = fields.Selection([
        ('unspecified', 'Unspecified'), ('returns', "Returns"),
        ('com_return', 'Commercial Discount'), ('discount', 'Allowed Discount')
    ])

    @api.onchange('taxation_percent', 'deduction_payment_type')
    def _onchange_taxation_percent(self):
        """
        on change taxation percent to change amount of deduction
        """
        if self.deduction_payment_type == 'percentage':
            self.taxation_amount = (self.total_taxation_amount *
                                    self.taxation_percent) / 100
        elif self.deduction_payment_type == 'full':
            self.taxation_amount = self.residual_taxation_amount

    @api.depends('journal_id')
    def _compute_payment_method_fields(self):
        """ compute payment method fields """
        moves = self.env['account.move'].browse(
            self.env.context.get('active_ids', []))
        payment_type = 'outbound'
        if moves and moves[0].move_type in ['out_invoice', 'in_refund']:
            payment_type = 'inbound'

        for pay in self:
            if payment_type == 'inbound':
                pay.available_payment_method_ids = pay.journal_id.\
                    inbound_payment_method_ids
            else:
                pay.available_payment_method_ids = pay.journal_id.\
                    outbound_payment_method_ids
            pay.hide_payment_method = len(
                pay.available_payment_method_ids
            ) == 1 and pay.available_payment_method_ids.code == 'manual'

    @api.depends('journal_id')
    def _compute_payment_method_id(self):
        """ compute payment method """
        for rec in self:
            moves = self.env['account.move'].browse(
                self.env.context.get('active_ids', []))
            payment_type = 'outbound'
            if moves and moves[0].move_type in ['out_invoice', 'in_refund']:
                payment_type = 'inbound'

            if payment_type == 'inbound':
                available_payment_methods = rec.journal_id. \
                    inbound_payment_method_ids
            else:
                available_payment_methods = rec.journal_id. \
                    outbound_payment_method_ids

            # Select the first available one by default.
            if available_payment_methods:
                rec.payment_method_id = available_payment_methods[0]._origin
            else:
                rec.payment_method_id = False

    # pylint: disable=too-many-locals
    def _get_payment_vals(self):
        """ prepare payments values """
        moves = self.env['account.move'].browse(
            self.env.context.get('active_ids', []))
        partner_type = 'supplier'
        payment_type = 'outbound'
        if self.tax_type == 'withholding':
            partner_type = 'customer'
            payment_type = 'inbound'
        update_credit = payment_type == 'outbound'
        update_debit = payment_type == 'inbound'

        # generate payment vals
        vals = []
        for rec in moves:
            taxation_amount = self.taxation_amount
            if self.deduction_payment_type == 'full' and len(moves) > 1:
                taxation_amount = rec.deduction_tax_residual_amount
            val = {
                'partner_type': partner_type, 'payment_type': payment_type,
                'journal_id': self.journal_id.id, 'tax_type': self.tax_type,
                'payment_method_id': self.payment_method_id.id,
                'currency_id': self.currency_id.id,
                'date': self.payment_date, 'ref': self.ref,
                'deduction_payment_type': self.deduction_payment_type,
                'taxation_amount': taxation_amount,
                'total_taxation_amount': rec.deduction_tax_total_amount,
                'residual_taxation_amount': rec.deduction_tax_residual_amount,
                'taxation_percent': self.taxation_percent,
                'deduction_type': self.deduction_type,
                'deduction_invoice_id': rec.id, 'partner_id': rec.partner_id.id,
            }
            new_payment = self.env['account.payment'].new(val)
            amount = abs(taxation_amount)
            balance = self.currency_id._convert(
                amount, self.company_id.currency_id,
                self.company_id, self.payment_date)
            currency_id = self.currency_id.id
            balance = self.company_id.currency_id.round(balance)
            payment_display_name = {
                'outbound-customer': _("Customer Reimbursement"),
                'inbound-customer': _("Customer Payment"),
                'outbound-supplier': _("Vendor Payment"),
                'inbound-supplier': _("Vendor Reimbursement"),
            }
            default_line_name = self.env[
                'account.move.line']._get_default_line_name(
                    payment_display_name[
                        '%s-%s' % (payment_type, partner_type)],
                    amount, self.currency_id, self.payment_date,
                    partner=rec.partner_id)
            total_receivable, total_liquidity = 0, 0
            line_vals_list = [
                # Receivable / Payable.
                (0, 0, {
                    'name': default_line_name, 'partner_id': rec.partner_id.id,
                    'date_maturity': self.payment_date,
                    'amount_currency': amount if self.currency_id else 0.0,
                    'currency_id': currency_id,
                    'debit': update_credit and balance or 0.0,
                    'credit': update_debit and balance or 0.0,
                    'account_id': new_payment.destination_account_id.id,
                })]
            total_receivable = abs(balance)

            for line in new_payment.deduction_line_ids:
                # Liquidity line.
                account_id = False
                account = line.deduction_tax_id.mapped(
                    'invoice_repartition_line_ids.account_id')
                if account:
                    account_id = account.id
                else:
                    raise UserError(
                        _('Missing required account in %s.') %
                        line.deduction_tax_id.name)
                amount = self.currency_id.round(-line.tax_amount)
                balance = self.currency_id._convert(
                    amount, self.company_id.currency_id,
                    self.company_id, self.payment_date)
                balance = self.company_id.currency_id.round(balance)
                total_liquidity += balance
                if line == new_payment.deduction_line_ids[-1]:
                    diff = total_receivable - total_liquidity
                    if diff and diff < 0.2:
                        balance += total_receivable - total_liquidity
                default_line_name = self.env[
                    'account.move.line']._get_default_line_name(
                        self.tax_type, amount, self.currency_id,
                        self.payment_date, partner=rec.partner_id)
                line_vals_list.append((0, 0, {
                    'name': default_line_name, 'partner_id': rec.partner_id.id,
                    'date_maturity': self.payment_date,
                    'amount_currency': amount if update_debit else -amount,
                    'currency_id': currency_id, 'account_id': account_id,
                    'debit': 0 if update_credit else balance,
                    'credit': balance if update_credit else 0,
                    'entry_deduction_tax_id': line.deduction_tax_id.id,
                }))
            val.update({'line_ids': line_vals_list})
            vals.append(val)
        return vals

    def create_payment(self):
        """ action post payment """
        self.ensure_one()
        vals = self._get_payment_vals()
        for val in vals:
            payment = self.env['account.payment'].with_context({
                'skip_account_move_synchronization': True,
            }).create(val)
            payment.action_post()
            domain = [('account_internal_type', 'in', (
                'receivable', 'payable')), ('reconciled', '=', False)]
            lines = payment.deduction_invoice_id.line_ids
            payment_lines = payment.line_ids.filtered_domain(domain)
            for account in payment_lines.account_id:
                (payment_lines + lines).filtered_domain(
                    [('account_id', '=', account.id),
                     ('reconciled', '=', False)]).reconcile()
        return {'type': 'ir.actions.act_window_close'}
