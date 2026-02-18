"""inherit account move"""

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    """
    inherit account move
    to apply calculation of deduction tax on invoice
    """
    _inherit = "account.move"

    deduction_tax_line_ids = fields.One2many(
        'account.move.deduction.line', 'move_id', string="Deduction Taxes",
        compute='_compute_deduction_tax_line_ids', store=True)
    deduction_tax_residual_amount = fields.Monetary(
        compute='_compute_deduction_tax_amount', store=True)
    deduction_tax_total_amount = fields.Monetary(
        compute='_compute_deduction_tax_amount',
        string="Total Allowance amount", store=True)
    invoice_filter_type_ded_domain = fields.Char(
        compute='_compute_invoice_filter_type_ded_domain')
    deduction_payment_ids = fields.One2many(
        'account.payment', 'deduction_invoice_id')

    @api.depends(
        'deduction_tax_line_ids', 'deduction_tax_line_ids.tax_amount',
        'deduction_tax_line_ids.paid_amount')
    def _compute_deduction_tax_amount(self):
        """
        compute deduction tax residual amount and total amount on invoice
        """
        for move in self:
            lines = move.mapped('deduction_tax_line_ids')
            move.deduction_tax_total_amount = sum(lines.mapped('tax_amount'))
            move.deduction_tax_residual_amount = \
                move.deduction_tax_total_amount - sum(
                    lines.mapped('paid_amount'))

    @api.depends('line_ids.price_subtotal', 'line_ids.deduction_tax_id')
    def _compute_deduction_tax_line_ids(self):
        """
        compute lines of deduction taxes
        """
        for move in self:
            move.deduction_tax_line_ids = False
            deduction_line = self.env['account.move.deduction.line']
            tax_lines = move.line_ids.filtered(
                lambda line: line.deduction_tax_id)
            if tax_lines:
                tax_grouped = {}
                for line in tax_lines:
                    if line.deduction_tax_id not in tax_grouped:
                        tax_grouped[line.deduction_tax_id] = {
                            'move_id': move.id,
                            'deduction_tax_id': line.deduction_tax_id.id,
                            'base_amount': line.price_subtotal,
                            'total_amount': line.price_total,
                            'tax_amount': line.deduction_tax_amount,
                        }
                    else:
                        tax_grouped[line.deduction_tax_id]['base_amount'] \
                            += line.price_subtotal
                        tax_grouped[line.deduction_tax_id]['tax_amount'] \
                            += line.deduction_tax_amount
                        tax_grouped[line.deduction_tax_id]['total_amount'] \
                            += line.price_total
                for tax in tax_grouped.values():
                    deduction_line.create(tax)

    # pylint: disable=no-member,inconsistent-return-statements
    def action_invoice_register_deduct(self):
        """
        action register deduct to open action of deduction payment
        :return: action of deduction wizard
        """
        invoices = self or self.browse(self.env.context.get('active_ids'))
        if not invoices:
            return
        # filter the selected ap invoices
        if invoices:
            for invoice in invoices:
                if invoice.state != 'posted' or \
                        invoice.deduction_tax_residual_amount == 0 or \
                        (invoice.move_type not in ['in_invoice', 'in_refund']
                         and len(invoices) > 1) or \
                        invoice.payment_state == 'paid':
                    raise UserError(_(
                        'You can only apply Taxes allowances on posted, not '
                        'fully taxed, and not paid vendor invoices.'))

            # display bulk deduction, in case of multi filtered invoices
            tax_type = ''
            deduction_payment_type = ''
            if invoices[0].move_type in ['in_invoice', 'in_refund']:
                tax_type = 'deduction'
                deduction_payment_type = 'full'
            elif invoices[0].move_type in ['out_invoice', 'out_refund']:
                tax_type = 'withholding'
                deduction_payment_type = 'amount'
            ctx = dict(self.env.context)
            residual = sum(invoices.mapped('deduction_tax_residual_amount'))
            total = sum(invoices.mapped('deduction_tax_total_amount'))
            ctx.update({
                'active_ids': invoices.ids, 'active_model': 'account.move',
                'default_tax_type': tax_type, 'taxation': True,
                'default_deduction_payment_type': deduction_payment_type,
                'default_company_id': invoices[0].company_id.id,
                'default_taxation_amount': residual,
                'default_residual_taxation_amount': residual,
                'default_total_taxation_amount': total,
                'default_edit_payment': tax_type == 'deduction' and len(
                    invoices) == 1,
                'default_currency_id': invoices[0].currency_id.id
            })
            # get journal default value
            journal_ids = self.env['account.journal'].search(
                [('company_id', '=', self.env.company.id),
                 ('taxation', '=', True), ('tax_type', '=', tax_type),
                 ('type', 'in', ('bank', 'cash'))], limit=1)
            if journal_ids:
                ctx.update({'default_journal_id': journal_ids[0].id})
            else:
                raise UserError(_(
                    'Please create deduction/withholding journal first'))

            # pylint: disable=protected-access
            return {
                'name': _('Register Deduction/Withholding Tax Payment'),
                'res_model': "deduction.register.payment.wizard",
                'view_mode': 'form', 'context': ctx,
                'target': 'new', 'type': 'ir.actions.act_window'}

    def action_view_payments(self):
        """
        This function returns an action that display existing payments
        of given account move.
        When only one found, show the payment immediately.
        """
        if self.move_type in ('in_invoice', 'in_refund'):
            action = self.env.ref('account.action_account_payments_payable')
        else:
            action = self.env.ref('account.action_account_payments')

        result = action.sudo().read()[0]
        payments = self._get_reconciled_payments()
        # choose the view_mode accordingly
        if len(payments) == 1:
            res = self.env.ref('account.view_account_payment_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = payments.id
        else:
            result['domain'] = [('id', 'in', payments.ids)]
        return result

    # pylint: disable=protected-access
    @api.onchange('invoice_date')
    def _onchange_invoice_date(self):
        """
        Onchange invoice_date
        """
        res = super(AccountMove, self)._onchange_invoice_date()
        for line in self.invoice_line_ids:
            deduction_tax_id = line.deduction_tax_id
            if deduction_tax_id and line.move_id.fiscal_position_id:
                deduction_tax_id = line.move_id.fiscal_position_id.map_tax(
                    deduction_tax_id,
                    partner=line.partner_id,
                    date=self.invoice_date
                )
            line.deduction_tax_id = deduction_tax_id
        return res

    @api.depends('move_type')
    def _compute_invoice_filter_type_ded_domain(self):
        """
        Compute invoice_filter_type_ded_domain
        """
        for move in self:
            if move.invoice_filter_type_domain == 'sale':
                move.invoice_filter_type_ded_domain = 'withholding'
            elif move.invoice_filter_type_domain == 'purchase':
                move.invoice_filter_type_ded_domain = 'deduction'
            else:
                move.invoice_filter_type_ded_domain = ''
