""" Update object hr.payslip """

from odoo import api, fields, models


# pylint: disable=protected-access
class HrPayslip(models.Model):
    """ Update object hr.payslip """
    _inherit = "hr.payslip"

    payment_line_ids = fields.One2many(
        comodel_name='hr.payslip.payment.order.line',
        inverse_name='payslip_id',
        copy=False,
    )
    paid_amount = fields.Monetary(
        compute='_compute_paid_amount',
        compute_sudo=True,
    )
    is_paid = fields.Boolean(
        compute='_compute_paid_amount',
        store=True,
        compute_sudo=True,
    )
    payment_method_ids = fields.Many2many(
        comodel_name='hr.payslip.payment.method',
        compute='_compute_payment_method',
    )
    bank_account_id = fields.Many2one(
        comodel_name='res.partner.bank',
        compute='_compute_bank_account',
        store=True,
        readonly=False,
    )
    bank_id = fields.Many2one(
        comodel_name='res.bank',
        compute='_compute_bank_account',
        store=True,
        readonly=False,
    )
    payment_count = fields.Integer(
        compute='_compute_payment_count',
        readonly=True,
    )

    @api.depends('employee_id')
    def _compute_bank_account(self):
        """
        update bank account
        """
        for record in self:
            record.bank_account_id = record.employee_id.bank_account_id
            record.bank_id = record.employee_id.bank_account_id.bank_id

    def _compute_paid_amount(self):
        """
        get sum paid amount
        """
        for record in self:
            paid_amount = sum(
                record.payment_line_ids.filtered(
                    lambda line: line.payment_id.state in ['draft', 'validated']
                ).mapped('paid_amount'))
            record.paid_amount = paid_amount
            net_wage = record._get_salary_line_total('NET')
            record.is_paid = bool(paid_amount >= net_wage)

    @api.depends('payment_line_ids', 'payment_line_ids.payment_id',
                 'payment_line_ids.payment_id.payment_method_id')
    def _compute_payment_method(self):
        """
        get payment method related to payslip
        """
        for record in self:
            record.payment_method_ids = record.mapped(
                'payment_line_ids.payment_id.payment_method_id')

    def action_open_payment(self):
        """
        open payment form or list related to payslip
        """
        payments = self.mapped('payment_line_ids.payment_id')
        action = self.env["ir.actions.actions"]._for_xml_id(
            "hr_payroll_payment_order.hr_payslip_payment_order_action")
        if len(payments) == 1:
            form_view = [(self.env.ref(
                'hr_payroll_payment_order.hr_payslip_payment_order_form').id,
                          'form')]
            if 'views' in action:
                action['views'] = form_view + \
                                  [(state, view) for state, view in
                                   action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = payments.id
        if len(payments) > 1:
            action['domain'] = [('id', 'in', payments.ids)]
        else:
            action = {'type': 'ir.actions.act_window_close'}

        context = {
            'create': False,
        }
        action['context'] = context
        return action

    def _compute_payment_count(self):
        """
        count number of payment
        """
        for record in self:
            record.payment_count = \
                len(record.mapped('payment_line_ids.payment_id'))
