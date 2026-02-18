""" Initialize Hr Loan to request loan """
from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class HrLoan(models.Model):
    """
        Initialize Hr Loan model:
         - request loans and validate the request data from configuration
    """
    _name = 'hr.loan'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Loan Request'
    _check_company_auto = True

    state = fields.Selection(
        [('draft', 'Draft'),
         ('waiting_approval_1', 'Submitted'),
         ('waiting_approval_2', 'First Approved'),
         ('approve', 'Approved'),
         ('refuse', 'Refused'),
         ('cancel', 'Canceled')], default='draft', tracking=True, copy=False)
    name = fields.Char(default='New', readonly=True)
    date = fields.Date(default=fields.Date.today(), readonly=True,
                       required=True, states={'draft': [('readonly', False)]})
    employee_id = fields.Many2one(
        'hr.employee', required=True, check_company=True,
        default=lambda self: self.env['hr.employee'].search(
            [('user_id', '=', self.env.uid)], limit=1),
        readonly=True, states={'draft': [('readonly', False)]}, )
    partner_id = fields.Many2one(
        'res.partner', related='employee_id.address_home_id', store=True
    )
    department_id = fields.Many2one(
        'hr.department')
    job_position = fields.Many2one(
        'hr.job')
    loan_amount = fields.Monetary(currency_field='currency_id',
                                  readonly=True,
                                  states={'draft': [('readonly', False)]})
    installment = fields.Integer(string='No Of Installments', default=1,
                                 readonly=True,
                                 states={'draft': [('readonly', False)]})
    account_payable_id = fields.Many2one(
        'account.account',
        related='partner_id.property_account_payable_id', store=True,
    )
    loan_account_id = fields.Many2one(
        'account.account', check_company=True, readonly=True,
        states={'draft': [('readonly', False)],
                'waiting_approval_1': [('readonly', False)],
                'waiting_approval_2': [('readonly', False)]},
        default=lambda self: self.env.company.loan_account_id.id,
    )
    journal_id = fields.Many2one(
        'account.journal', check_company=True, readonly=True,
        states={'draft': [('readonly', False)],
                'waiting_approval_1': [('readonly', False)],
                'waiting_approval_2': [('readonly', False)]},
        domain=[('type', '=', 'general')],
        default=lambda self: self.env.company.loan_journal_id.id,
    )
    account_move_id = fields.Many2one(
        'account.move', copy=False, string='Journal Entry',
        readonly=True, check_company=True
    )
    payments_paid = fields.Boolean(default=False, copy=False, readonly=True)
    payment_date = fields.Date(
        string='Payment Start Date', required=True, default=fields.Date.today(),
        readonly=True, states={'draft': [('readonly', False)]}
    )
    company_id = fields.Many2one(
        'res.company', default=lambda self: self.env.company,
        readonly=True, states={'draft': [('readonly', False)]}
    )
    currency_id = fields.Many2one(
        'res.currency', required=True, readonly=True,
        default=lambda self: self.env.company.currency_id)
    total_amount = fields.Float(readonly=True, compute='_compute_loan_amount')
    balance_amount = fields.Float(compute='_compute_loan_amount')
    total_paid_amount = fields.Float(compute='_compute_loan_amount')
    loan_line_ids = fields.One2many(
        'hr.loan.line', 'loan_id', string='Installments', index=True,
        readonly=True, states={'draft': [('readonly', False)],
                               'waiting_approval_1': [('readonly', False)],
                               'waiting_approval_2': [('readonly', False)]})

    def _compute_loan_amount(self):
        """ compute total_amount, balance_amount and total_paid_amount """
        for loan in self:
            total_paid = sum(loan.loan_line_ids.filtered(
                lambda r: r.paid).mapped('amount'))
            balance_amount = loan.loan_amount - total_paid
            self.total_amount = loan.loan_amount
            self.balance_amount = balance_amount
            self.total_paid_amount = total_paid

    def generate_installment(self):
        """ generate loan installment """
        for loan in self:
            loan.loan_line_ids.unlink()
            date_start = datetime.strptime(str(loan.payment_date),
                                           '%Y-%m-%d')
            amount = round((loan.loan_amount / loan.installment), 0)
            lines_amount = 0
            for i in range(1, loan.installment + 1):
                if i == loan.installment and loan.loan_amount > 1:
                    amount = loan.loan_amount - lines_amount
                lines_amount += amount
                self.env['hr.loan.line'].create({
                    'date': date_start,
                    'amount': amount,
                    'employee_id': loan.employee_id.id,
                    'loan_id': loan.id})
                date_start = date_start + relativedelta(months=1)

    def action_refuse(self):
        """ Refuse loan request """
        return self.write({'state': 'refuse'})

    def action_submit(self):
        """ Submit loan request """
        self.validate()
        self._notify_loan_approval()
        self.write({'state': 'waiting_approval_1'})

    def _notify_loan_approval(self):
        """ create activity when employee submit loan """
        for rec in self:
            responsible = rec.company_id.loan_hr_user_id \
                          or self.env.company.loan_hr_user_id
            if responsible:
                rec.activity_schedule(
                    'hr_loan.mail_act_loan_approval',
                    user_id=responsible.id)

    def action_cancel(self):
        """ Cancel loan request """
        self.write({'state': 'cancel'})

    def action_approve(self):
        """ Approve loan request """
        for loan in self:
            if not loan.loan_line_ids:
                raise UserError(
                    _('You must compute installment before Approved'))
            if self.env.company.loan_approve:
                self.write({'state': 'waiting_approval_2'})
            else:
                self.action_double_approve()

    def unlink(self):
        """ Override to restrict delete if the loan not draft or canceled """

        for loan in self:
            if loan.state not in ('draft', 'cancel'):
                raise UserError(_('You cannot delete a loan which is not '
                                  'in draft or cancelled state'))
        return super().unlink()

    def validate_multiple_loans(self):
        """ Validate multiple loans when loan.allow_multiple is enabled """
        for loan in self:
            company = self.env.company
            if company.loan_type and company.loan_max:
                unpaid_lines = sum(self.env['hr.loan.line'].sudo().search([
                    ('employee_id', '=', loan.employee_id.id),
                    ('paid', '=', False), ('loan_id.state', '=', 'approve'),
                ]).mapped('amount'))
                new_max = 0
                if company.loan_type == 'amount':
                    new_max = company.loan_max - unpaid_lines
                elif company.loan_type == 'percentage':
                    contract = loan.employee_id.sudo().contract_id
                    new_max = (contract.wage * company.loan_max
                               / 100) - unpaid_lines
                if loan.loan_amount > new_max:
                    raise UserError(
                        _("Loan amount can't be greater than %d") % new_max
                    )

    def validate(self):
        """
            Validate loan request:
             - Check if the request matches the configurations.
        """
        company = self.env.company
        for loan in self:
            contract = loan.employee_id.sudo().contract_id
            if not contract or (contract and contract.state != 'open'):
                raise UserError(_("You must have running contract"))
            # there are 2 ways of validation on loan_max
            # depends on  loan_allow_multiple is True or False
            if company.loan_allow_multiple:
                loan.validate_multiple_loans()
            elif company.loan_type and company.loan_max:
                if company.loan_type == 'amount' and \
                        loan.loan_amount > company.loan_max:
                    raise UserError(
                        _("Loan amount can't be greater than %d") %
                        company.loan_max
                    )
                if company.loan_type == 'percentage':
                    loan_max_computed = contract.wage * company.loan_max / 100
                    if loan.loan_amount > loan_max_computed:
                        raise UserError(
                            _("Loan amount can't be greater than %d") %
                            loan_max_computed
                        )
            if company.loan_max_months and \
                    loan.installment > company.loan_max_months:
                raise UserError(
                    _("NO of installment can't be greater than %d") %
                    company.loan_max_months
                )
            if company.loan_contract_months:
                allowed_date = \
                    loan.employee_id.contract_id.first_contract_date \
                    + relativedelta(months=company.loan_contract_months)
                if allowed_date > loan.date:
                    raise UserError(_(
                        "%d Months should passed from the start of your "
                        "contract to request a loan"
                    ) % company.loan_contract_months)

    # pylint: disable=arguments-differ
    @api.model
    def create(self, values):
        """ Override to check multiple loan """
        company = self.env.company
        values['name'] = self.env['ir.sequence'].next_by_code('hr.loan') or '/'
        if not company.loan_allow_multiple:
            approved_loans = self.env['hr.loan'].search([
                ('employee_id', '=', values.get('employee_id')),
                ('state', '=', 'approve'),
            ])
            loans = approved_loans.filtered(lambda x: x.balance_amount)
            if loans:
                raise UserError(
                    _("The employee has already a pending installment"))
        return super().create(values)

    def validate_amount(self):
        """ Validate total amount of lines. """
        for loan in self:
            total_lines = sum(loan.mapped('loan_line_ids').mapped('amount'))
            if total_lines != loan.loan_amount:
                raise UserError(
                    _('Total amount of lines not equal loan amount'))

    @api.constrains('loan_line_ids')
    def _check_total_loan_line_ids(self):
        """ Validate loan total amount on state approved. """
        for loan in self:
            if loan.state == 'approve':
                loan.validate_amount()

    def check_loans(self):
        """ Check Loans accounting accounts. """
        for loan in self:
            if not loan.loan_account_id:
                raise UserError(_('You must enter Loan Account to approve.'))
            if not loan.journal_id:
                raise UserError(_('You must enter journal to approve.'))
            if not loan.account_payable_id:
                raise UserError(_('You must enter address with Account Payable'
                                  ' for employee to approve.'))
            if loan.journal_id.type != 'general':
                raise UserError(
                    _('You must choose journal with type Miscellaneous.'))

    def action_double_approve(self):
        """
            This create account move for request
            in case of double approval.
        """
        self.check_loans()
        for loan in self.sudo():
            loan.validate_amount()
            amount = loan.loan_amount
            loan_name = loan.employee_id.name
            journal_id = loan.journal_id.id
            credit_account_id = loan.account_payable_id.id
            debit_account_id = loan.loan_account_id.id
            debit_vals = {
                'name': loan_name,
                'partner_id': loan.partner_id.id,
                'account_id': debit_account_id,
                'journal_id': journal_id,
                'date': fields.Date.today(),
                'debit': amount > 0.0 and amount or 0.0,
                'credit': amount < 0.0 and -amount or 0.0,
                'loan_id': loan.id,
            }
            credit_vals = {
                'name': loan_name,
                'partner_id': loan.partner_id.id,
                'account_id': credit_account_id,
                'journal_id': journal_id,
                'date': fields.Date.today(),
                'debit': amount < 0.0 and -amount or 0.0,
                'credit': amount > 0.0 and amount or 0.0,
                'loan_id': loan.id,
            }
            vals = {
                'narration': loan_name,
                'ref': 'Loan %s For (%s)' % (loan.name, loan_name),
                'journal_id': journal_id,
                'date': fields.Date.today(),
                'line_ids': [(0, 0, debit_vals), (0, 0, credit_vals)]
            }
            move = self.env['account.move'].create(vals)
            move.action_post()
            loan.account_move_id = move.id
        self.write({'state': 'approve'})
        return True

    def set_to_paid(self):
        """ Set Paid """
        self.write({'payments_paid': True})

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        """ update department and job """
        for rec in self:
            rec.department_id = rec.employee_id.department_id
            rec.job_position = rec.employee_id.job_id
