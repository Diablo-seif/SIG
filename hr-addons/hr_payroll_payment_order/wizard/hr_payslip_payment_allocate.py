""" init hr.payslip.payment.allocate """
from odoo import _, fields, models
from odoo.exceptions import UserError


# pylint: disable=no-member,protected-access,no-self-use,cell-var-from-loop
class HrPayslipPaymentAllocate(models.TransientModel):
    """
     init hr.payslip.payment.allocate
    """
    _name = 'hr.payslip.payment.allocate'
    _description = 'HR Payslip Payment Allocate Wizard'

    payment_order_id = fields.Many2one(
        comodel_name='hr.payslip.payment.order',
        domain="[('state', '=', 'draft')]",
    )
    payment_method_id = fields.Many2one(
        comodel_name='hr.payslip.payment.method',
    )
    mode = fields.Selection(
        selection=[('existing', 'an existing payment order'),
                   ('new', 'a new payment order')],
        default='existing',
    )
    change_payment_method = fields.Boolean(
        default=True,
        help='Force move payslips from old payment order to new order.'
    )

    def allocate_payments(self):
        """
        create / update payment order line
        """
        self.ensure_one()
        old_payslips = self.env['hr.payslip']
        payslips = self.env['hr.payslip'].browse(
            self.env.context.get('active_ids'))
        if not self.change_payment_method:
            payslips = payslips.filtered(lambda line: not line.is_paid)
            if not payslips:
                raise UserError(_('No payslip selected need to paid!'))
        if any(payslip.state not in ['done', 'verify'] for payslip in payslips):
            raise UserError(_(
                'Please confirm payslip before adding to payment'))
        if any(payslip.is_paid and payslip.state in ['done', 'verify'] and any(
                pay.payment_id.state == 'validated' for pay in
                payslip.payment_line_ids) for payslip in payslips):
            raise UserError(_('You can not add paid payslip'))
        if self.change_payment_method:
            payslips.mapped('payment_line_ids').unlink()
        if self.mode == 'new':
            company = payslips.company_id
            if len(company) > 1:
                raise UserError(
                    _("The selected payslip should belong "
                      "to an unique company."))
            self.env['hr.payslip.payment.order'].create({
                'payment_method_id': self.payment_method_id.id,
                'company_id': company.id,
                'line_ids': [(0, 0, {
                    'payslip_id': payslip.id,
                    'paid_amount': payslip.net_wage - payslip.paid_amount,
                }) for payslip in payslips]
            })
        else:
            for payslip in payslips:
                payment_line = self.payment_order_id.line_ids.filtered(
                    lambda payslip_line: payslip_line.payslip_id == payslip)
                if payment_line:
                    payment_line.paid_amount += \
                        payslip.net_wage - payslip.paid_amount
                    old_payslips |= payslip
            if payslips:
                self.payment_order_id.write({
                    'line_ids': [(0, 0, {
                        'payslip_id': payslip.id,
                        'paid_amount': payslip.net_wage - payslip.paid_amount,
                    }) for payslip in payslips - old_payslips]
                })
