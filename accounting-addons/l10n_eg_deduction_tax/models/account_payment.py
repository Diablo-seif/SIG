"""inherit account payment"""

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountPayment(models.Model):
    """
    inherit account.payment to add register deduction feature

    """
    _inherit = 'account.payment'

    tax_type = fields.Selection([
        ('deduction', 'Deduction'), ('withholding', 'Withholding')])
    total_taxation_amount = fields.Monetary()
    residual_taxation_amount = fields.Monetary()
    taxation_amount = fields.Monetary()
    deduction_payment_type = fields.Selection(
        [('full', 'Full'), ('percentage', 'Percentage'), ('amount', 'Amount')])
    taxation_percent = fields.Float()
    amount_in_words = fields.Char(compute="_compute_amount_in_words")
    deduction_type = fields.Selection([
        ('unspecified', 'Unspecified'), ('returns', "Returns"),
        ('com_return', 'Commercial Discount'), ('discount', 'Allowed Discount')
    ])
    deduction_line_ids = fields.One2many(
        'account.payment.deduction.line', 'payment_id',
        compute='_compute_deduction_line_ids', store=True)
    deduction_invoice_id = fields.Many2one('account.move')

    def action_post(self):
        """
        overloading action_post method to set amount from taxation amount
        in case of deduction taxes
        """
        for rec in self:
            if rec.taxation_amount and rec.tax_type:
                if rec.taxation_amount < rec.residual_taxation_amount:
                    raise UserError(_(
                        "You can't pay amount more than the residual"))
                rec.amount = - sum(rec.mapped(
                    'deduction_line_ids').mapped('tax_amount'))
                rec.taxation_percent = (rec.taxation_amount /
                                        rec.total_taxation_amount) * 100
                deduction_lines = rec.mapped(
                    'deduction_invoice_id').mapped('deduction_tax_line_ids')
                for line in deduction_lines:
                    paid_amount = (line.tax_amount * rec.taxation_percent) / 100
                    line.paid_amount += line.currency_id.round(paid_amount)
            elif rec.taxation_amount == 0 and rec.tax_type:
                rec.amount = 0

        # pylint: disable=no-member
        return super(AccountPayment, self).action_post()

    # pylint: disable=no-member
    def _compute_hide_payment_method(self):
        """
        overload to hide payment method from form if there is deduction type
        """
        res = super(AccountPayment, self)._compute_hide_payment_method()
        for payment in self:
            if payment.tax_type:
                payment.hide_payment_method = True
        return res

    # pylint: disable=protected-access
    def get_deduction_lines(self):
        """
        helper method to get deduction lines from payment
        :return: list of dictionaries for all taxes if exist
         every dictionary for tax type have :
         deduction_tax_id , tax_amount, base_amount, total_amount, payment_id
        """
        if not self.deduction_invoice_id:
            return []
        deduction_ids = self.deduction_invoice_id.mapped(
            'deduction_tax_line_ids')
        res = []
        for line in deduction_ids:
            if self.deduction_payment_type != 'percentage':
                self.taxation_percent = (self.taxation_amount /
                                         self.total_taxation_amount) * 100
            paid_amount = self.taxation_percent * line.tax_amount / 100
            base_amount = line.base_amount * self.taxation_percent / 100
            total_amount = line.total_amount * self.taxation_percent / 100

            # if user change currency of payment
            if line.currency_id != self.currency_id:
                paid_amount = line.currency_id._convert(
                    paid_amount, self.currency_id,
                    self.company_id, self.payment_date)
                base_amount = line.currency_id._convert(
                    base_amount, self.currency_id,
                    self.company_id, self.payment_date)
                total_amount = line.currency_id._convert(
                    total_amount, self.currency_id,
                    self.company_id, self.payment_date)
            res.append({
                'deduction_tax_id': line.deduction_tax_id.id,
                'tax_amount': self.currency_id.round(paid_amount),
                'base_amount': self.currency_id.round(base_amount),
                'total_amount': self.currency_id.round(total_amount),
                'payment_id': self.id,
            })
        return res

    def _compute_amount_in_words(self):
        """
        compute amount of payment in words
        """
        for rec in self:
            rec.amount_in_words = rec.currency_id.with_context(
                lang=rec.partner_id.lang or 'en_US').amount_to_text(rec.amount)

    @api.depends('tax_type', 'taxation_amount')
    def _compute_deduction_line_ids(self):
        """
        compute deduction_line_ids depends on tax_type and taxation_amount
        using helper method get_deduction_lines
        """
        deduction_line = self.env['account.payment.deduction.line'].sudo()
        for rec in self:
            rec.write({'deduction_line_ids': [(5, 0, 0)]})
            if rec.tax_type:
                res = rec.get_deduction_lines()
                if res:
                    deduction_line.create(res)
