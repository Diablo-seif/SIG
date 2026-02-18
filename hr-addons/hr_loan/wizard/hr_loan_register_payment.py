""" Register payment for loan request. """

# pylint: disable=no-name-in-module
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HrLoanRegisterPaymentWizard(models.TransientModel):
    """ Register payment for loan request. """
    _name = "hr.loan.register.payment.wizard"
    _description = "Loan Register Payment Wizard"

    @api.model
    def _default_partner_id(self):
        """
            Get Default Partner Form Active IDS.
            :return: partner_id <res.partner>
        """
        context = dict(self._context or {})
        active_ids = context.get('active_ids', [])
        loan = self.env['hr.loan'].browse(active_ids)
        return loan.sudo().employee_id.address_home_id.id

    @api.constrains('amount')
    def _check_amount(self):
        """ Check Amount """
        for rec in self:
            if not rec.amount > 0.0:
                raise ValidationError(
                    _("The payment amount must be strictly positive."))

    @api.depends('payment_method_id')
    def _compute_show_partner_bank(self):
        """ Computes if the destination bank account must be
        displayed in the payment form view. By default, it
        won't be displayed but some modules might change that,
        depending on the payment type.
        """
        for payment in self:
            payment_obj = self.env['account.payment']
            # pylint: disable=protected-access
            method = payment_obj._get_method_codes_using_bank_account()
            code_in_bool = payment.payment_method_id.code in method
            payment.show_partner_bank_account = code_in_bool

    @api.depends('journal_id')
    def _compute_hide_payment_method(self):
        """ Compute hide_payment_method """
        self.ensure_one()
        if not self.journal_id:
            self.hide_payment_method = True
            return
        journal_pay_methods = self.journal_id.outbound_payment_method_line_ids
        res = len(journal_pay_methods) == 1 and journal_pay_methods[0]. \
            code == 'manual'
        self.hide_payment_method = res

    @api.onchange('journal_id')
    def _onchange_journal(self):
        """ :return domain Onchange Journal """
        if self.journal_id:
            # Set default payment method
            # (we consider the first to be the default one)
            payment_methods = self.journal_id.outbound_payment_method_line_ids
            self.payment_method_id = \
                payment_methods[0] if payment_methods else False
            # Set payment method domain (restrict to methods enabled for
            # the journal and to selected payment type)
            return {'domain': {
                'payment_method_id': [('payment_type', '=', 'outbound'),
                                      ('id', 'in', payment_methods.ids)]}}
        return {}

    def _get_payment_vals(self):
        """ Get payment values for loan
        """
        return {
            'partner_type': 'supplier',
            'payment_type': 'outbound',
            'partner_id': self.partner_id.id,
            # 'partner_bank_account_id': self.partner_bank_account_id.id,
            'journal_id': self.journal_id.id,
            'company_id': self.company_id.id,
            'payment_method_line_id': self.payment_method_id.id,
            'amount': self.amount,
            'currency_id': self.currency_id.id,
            'date': self.payment_date,
            'ref': self.communication
        }

    def loan_post_payment(self):
        """ Post loan payment """
        self.ensure_one()
        context = dict(self._context or {})
        active_ids = context.get('active_ids', [])
        loan = self.env['hr.loan'].browse(active_ids)

        # Create payment and post it
        payment = self.env['account.payment'].create(self._get_payment_vals())
        payment.action_post()

        # Log the payment in the chatter
        body = (_("A payment of %(pay_amount)s %(currency_symbol)s with "
                  "the reference <a href='#' data-oe-model='%(model)s' "
                  "data-oe-id='%(pay_id)d'>%(pay_name)s</a>"
                  " related to your loan %(loan_name)s "
                  "has been made.") % {
                      "pay_amount": payment.amount,
                      "currency_symbol": payment.currency_id.symbol,
                      "model": 'account.payment',
                      "pay_id": payment.id,
                      "pay_name": payment.name,
                      "loan_name": loan.name
                  })
        loan.message_post(body=body)
        # Reconcile the payment and the loan,
        # i.e. lookup on the payable account move lines
        account_move_lines_to_reconcile = self.env['account.move.line']
        for line in payment.move_id.line_ids + loan.account_move_id.line_ids:
            if line.account_id.account_type == 'liability_payable' \
                    and not line.reconciled:
                account_move_lines_to_reconcile |= line
        account_move_lines_to_reconcile.reconcile()
        return {'type': 'ir.actions.act_window_close'}

    partner_id = fields.Many2one('res.partner', string='Partner', required=True,
                                 default=_default_partner_id)
    partner_bank_account_id = fields.Many2one('res.partner.bank',
                                              string="Recipient Bank Account")
    journal_id = fields.Many2one('account.journal', string='Payment Method',
                                 required=True,
                                 domain=[('type', 'in', ('bank', 'cash'))])
    company_id = fields.Many2one('res.company', related='journal_id.company_id',
                                 string='Company', readonly=True, required=True)
    payment_method_id = fields.Many2one('account.payment.method.line',
                                        string='Payment Type', required=True)
    amount = fields.Monetary(string='Payment Amount', required=True)
    currency_id = fields.Many2one(
        'res.currency', string='Currency', required=True,
        default=lambda self: self.env.user.company_id.currency_id
    )
    payment_date = fields.Date(default=fields.Date.context_today, required=True)
    communication = fields.Char(string='Memo')
    hide_payment_method = fields.Boolean(compute='_compute_hide_payment_method',
                                         help="Technical field used to hide the"
                                              " payment method if the selected "
                                              "journal has only one available "
                                              "which is 'manual'")
    show_partner_bank_account = fields.Boolean(
        compute='_compute_show_partner_bank',
        help='Technical field used to know whether the field '
             '`partner_bank_account_id` needs to be displayed or not in '
             'the payments form views'
    )
