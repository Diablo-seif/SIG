""" Initialize Payment Request """

import re

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


# pylint: disable=anomalous-backslash-in-string,no-self-use
class PaymentRequest(models.Model):
    """
        Initialize Payment Request:
    """
    _name = 'payment.request'
    _description = 'Payment Request'
    _check_company_auto = True
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.model
    def default_get(self, fields_list):
        """
        get default available_amount
        :param fields_list:
        :return:
        """
        res = super().default_get(fields_list)
        res['available_amount'] = self.get_available_amount()
        return res

    name = fields.Char(default='New')
    company_id = fields.Many2one(
        'res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one(
        'res.currency', default=lambda self: self.env.company.currency_id)
    user_id = fields.Many2one(
        'res.users', 'Responsible', default=lambda self: self.env.user)
    state = fields.Selection(
        [('draft', 'Draft'), ('submitted', 'Submitted'),
         ('confirm', 'Confirm')],
        default='draft', string='Status', tracking=True)
    line_ids = fields.One2many('payment.request.line', 'payment_request_id')
    total_due = fields.Monetary(compute='_compute_total_amount')
    total_approved = fields.Monetary(compute='_compute_total_amount')
    total_amount = fields.Monetary(compute='_compute_total_amount')
    pay_type = fields.Selection(
        [('percentage', 'Percentage'), ('amount', 'Amount')], default='amount')
    available_amount = fields.Monetary('Available Amount Cash/Bank')

    @api.depends('line_ids', 'line_ids.total_due',
                 'line_ids.total_payment_request',
                 'line_ids.approved_payment_amount')
    def _compute_total_amount(self):
        """ Compute total_amount value """
        for rec in self:
            approved = sum(rec.line_ids.mapped('approved_payment_amount'))
            rec.update({
                'total_due': sum(rec.line_ids.mapped('total_due')) - approved,
                'total_amount': sum(
                    rec.line_ids.mapped('total_payment_request')),
                'total_approved': approved,
            })

    @api.onchange('currency_id')
    def _onchange_currency_id(self):
        """ currency_id """
        self.line_ids.update({'currency_id': self.currency_id.id})

    @api.model
    def create(self, vals_list):
        """
            Override create method
             - sequence name
        """
        if vals_list.get('name', _('New')) == _('New'):
            sequence = self.env['ir.sequence'].next_by_code('payment.request')
            vals_list.update(name=sequence or '/')
        return super(PaymentRequest, self).create(vals_list)

    @api.model
    def extract_amount(self, formatted_amount):
        """ Extract Amount """
        regex = '[-+]?\d*\,\d+.\d+|\d+'  # noqa: W605
        matches = [float(n.replace(',', '')) for n in
                   re.findall(regex, formatted_amount)]
        return matches[0] if matches else 0

    @api.model
    def get_available_amount(self):
        """ Get Available Amount """
        journals = self.env['account.journal'].search(
            [('type', 'in', ['cash', 'bank'])])
        return sum(
            self.extract_amount(
                journal.get_journal_dashboard_datas().get('account_balance'))
            for journal in journals)

    def update_available_amount(self):
        """ Update Available Amount """
        for rec in self:
            rec.available_amount = self.get_available_amount()

    # pylint: disable=protected-access
    def action_submit(self):
        """ Action Submit """
        for rec in self:
            if not self.env.company.payment_request_responsible_id:
                raise ValidationError(
                    _('No payment request responsible, '
                      'Please contact your system administrator.'))
            rec.state = 'submitted'
            rec.line_ids.state = 'waiting'
            rec._activity_schedule_with_view(
                'mail.mail_activity_data_todo',
                views_or_xmlid='payment_request.payment_request_tree',
                user_id=self.env.company.payment_request_responsible_id.id,
                summary=_('Payment lines waiting for approval'),
            )

    def action_approve_all(self):
        """ Action Approve All """
        for rec in self:
            rec.line_ids.filtered(lambda r: r.state == 'waiting').write({
                'pay_type': 'percentage',
                'pay_amount': 100,
            })
            rec.line_ids.action_approve()
