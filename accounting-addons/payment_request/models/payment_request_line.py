""" Initialize Payment Request Line """

from odoo import _, api, fields, models


# pylint: disable=no-member
class PaymentRequestLine(models.Model):
    """
        Initialize Payment Request Line:
    """
    _name = 'payment.request.line'
    _description = 'Payment Request Line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'partner_id'

    partner_id = fields.Many2one(
        'res.partner'
    )
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id)
    total_due = fields.Monetary()
    total_payment_request = fields.Monetary()
    approve_date = fields.Date()
    last_request_amount = fields.Monetary()
    last_request_date = fields.Date()
    last_payment_amount = fields.Monetary()
    last_payment_date = fields.Date()
    approved_payment_amount = fields.Monetary()
    state = fields.Selection(
        [('draft', 'Draft'), ('waiting', 'Waiting Approval'),
         ('approved', 'Approved'), ('rejected', 'Rejected')],
        default='draft', string='Status')
    pay_type = fields.Selection(
        [('percentage', 'Percentage'), ('amount', 'Amount')],
        default='percentage')
    pay_amount = fields.Float()
    payment_request_id = fields.Many2one('payment.request')
    move_ids = fields.Many2many('account.move')

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        """ partner_id"""
        filtered_payments = self.partner_id.payment_request_line_ids.filtered(
            lambda r: r.approve_date and r.state == 'approved'and
            r.id != self._origin.payment_request_id)
        payments = filtered_payments.sorted(
            key=lambda r: r.approve_date, reverse=True)
        if payments:
            self.last_request_date = payments[0].approve_date
            self.last_request_amount = payments[0].approved_payment_amount

        account_payments = self.env['account.payment'].search([
            ('payment_type', '=', 'outbound'),
            ('partner_type', '=', 'supplier'), ('state', '=', 'posted'),
            ('partner_id', '=', self.partner_id.id),
        ]).sorted(key=lambda r: r.date)
        if account_payments:
            self.last_payment_amount = account_payments[-1].amount
            self.last_payment_date = account_payments[-1].date
        invoices = self.env['account.move'].search([
            ('partner_id', '=', self.partner_id.id),
            ('currency_id', '=', self.currency_id.id),
            ('state', '=', 'posted'), ('amount_residual', '>', 0),
            ('move_type', 'in', ['in_invoice', 'out_refund'])])
        self.total_due = sum(invoices.mapped('amount_residual'))

    def approve_payment_request_line(self):
        """ :return Payment Request Line action """
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'payment.request.line',
            'name': _('Approve Payment Line'),
            'view_mode': 'form',
            'context': {'form_view_initial_mode': 'edit', },
            'res_id': self.id,
            'target': 'new',
            'views': [(
                self.env.ref(
                    'payment_request.approve_payment_request_line_form').id,
                'form'
            )]
        }

    # pylint: disable=protected-access
    def action_approve(self):
        """ Action Approve """
        for rec in self:
            if rec.state == 'waiting':
                rec.state = 'approved'
                rec.approved_payment_amount = \
                    (rec.pay_amount if rec.pay_type == 'amount' else
                     rec.total_payment_request * rec.pay_amount / 100)
                rec.approve_date = fields.Date.today()
                rec._activity_schedule_with_view(
                    'mail.mail_activity_data_todo',
                    views_or_xmlid='payment_request.payment_request_line_form',
                    user_id=rec.payment_request_id.user_id.id,
                    summary=_('Payment request approved'),
                )
        return {'type': 'ir.actions.act_window_close'}

    def action_reject(self):
        """ Action Reject """
        for rec in self:
            rec.state = 'rejected'

    def action_view_account_move(self):
        """ :return Account Move action """
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'name': _('Bills'),
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.move_ids.ids)],
            'context': {'create': False, 'edit': False},
        }
