""" init hr.payslip.payment.order.line """
from odoo import api, fields, models


# pylint: disable=no-member,protected-access
class HrPayslipPaymentOrderLine(models.Model):
    """
    init hr.payslip.payment.order.line
    """
    _name = 'hr.payslip.payment.order.line'
    _description = 'Hr Payslip Payment Order Lines'
    _order = 'payment_id asc,payslip_id asc, id asc'

    payment_id = fields.Many2one(
        comodel_name='hr.payslip.payment.order',
        ondelete="cascade",
        required=True,
    )
    payment_method_id = fields.Many2one(
        comodel_name='hr.payslip.payment.method',
        related='payment_id.payment_method_id',
        store=True,
    )
    payslip_id = fields.Many2one(
        comodel_name='hr.payslip',
        required=True,
        ondelete="restrict",
    )
    payslip_run_id = fields.Many2one(
        comodel_name='hr.payslip.run',
        related='payslip_id.payslip_run_id',
        store=True,
    )
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        related='payslip_id.currency_id',
        store=True,
    )
    net_wage = fields.Monetary(
        compute='_compute_net',
        store=True,
    )
    paid_amount = fields.Monetary()

    @api.depends('payslip_id', 'payslip_id.line_ids')
    def _compute_net(self):
        """
        compute net amount based on salary rule
        """
        for record in self:
            net_wage = 0
            if record.payslip_id:
                net_wage = record.payslip_id._get_salary_line_total('NET')
            record.net_wage = net_wage

    @api.onchange('payslip_id')
    def _onchange_payslip(self):
        """
        update paid amount
        """
        paid_amount = 0
        if self.payslip_id:
            paid_amount = sum(self.payslip_id.payment_line_ids.filtered(
                lambda line: line.id != self.id).mapped('paid_amount'))
            paid_amount = self.payslip_id.net_wage - paid_amount
        self.paid_amount = paid_amount

    def copy_data(self, default=None):
        default = {'paid_amount': 0.0}
        return super(HrPayslipPaymentOrderLine, self).copy_data(default=default)
