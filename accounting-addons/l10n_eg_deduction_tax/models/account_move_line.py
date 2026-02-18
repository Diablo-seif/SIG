"""inherit account move line"""

from odoo import api, fields, models


# pylint: disable=no-member, protected-access
class AccountMoveLine(models.Model):
    """
    inherit account move line
    to add fields of tax allowance
    """
    _inherit = "account.move.line"

    def _get_deduction_tax(self):
        """
        Get deduction_tax
        """
        self.ensure_one()
        deduction_tax_id = self.env['account.tax']
        if self.move_id.move_type in ['in_invoice', 'in_refund']:
            deduction_tax_id = self.product_id.deduction_tax_id
        elif self.move_id.move_type in ['out_invoice', 'out_refund']:
            deduction_tax_id = self.product_id.withholding_tax_id
        return deduction_tax_id

    @api.onchange('product_id')
    def _onchange_product_id(self):
        """
        Override Onchange Product
        """
        res = super(AccountMoveLine, self)._onchange_product_id()
        for line in self:
            if not line.product_id or line.display_type in (
                    'line_section', 'line_note'):
                continue
            deduction_tax_id = line._get_deduction_tax()
            if deduction_tax_id:
                deduction_tax_id = line.move_id.fiscal_position_id.map_tax(
                    deduction_tax_id, partner=line.partner_id,
                    date=line.move_id.invoice_date)
            line.deduction_tax_id = deduction_tax_id
        return res

    @api.onchange('account_id')
    def _onchange_account_id(self):
        """
        Override Onchange Account
        """
        res = super(AccountMoveLine, self)._onchange_account_id()
        deduction_tax_id = self.deduction_tax_id
        if deduction_tax_id and self.move_id.fiscal_position_id:
            deduction_tax_id = self.move_id.fiscal_position_id.map_tax(
                deduction_tax_id, partner=self.partner_id,
                date=self.move_id.invoice_date)
            self.deduction_tax_id = deduction_tax_id
        return res

    @api.depends('product_id', 'price_subtotal', 'deduction_tax_id',
                 'move_id.partner_id', 'move_id.invoice_date')
    def _compute_deduction_tax(self):
        """
        compute deduction tax and deduction tax percent
        """
        for line in self:
            normal_compute = True
            partner_id = line.move_id.partner_id
            invoice_date = line.move_id.invoice_date
            if (
                    partner_id.deduction_tax_exemption_status and invoice_date
                    and partner_id.deduction_tax_exemption_status == 'advanced'
                    and partner_id.exemption_expire_date >= invoice_date
            ) or (partner_id.deduction_tax_exemption_status == 'exempt'):
                normal_compute = False
            percent = 0
            amount = 0
            if line.deduction_tax_id and normal_compute:
                percent = line.deduction_tax_id.amount
                amount = (percent * line.price_subtotal) / 100
            line.deduction_tax_percent = percent
            line.deduction_tax_amount = amount

    # pylint: disable=missing-return
    def _copy_data_extend_business_fields(self, values):
        """
        OVERRIDE copy_data_extend_business_fields
        """
        super(AccountMoveLine, self)._copy_data_extend_business_fields(values)
        values['deduction_tax_id'] = self.deduction_tax_id.id

    deduction_tax_id = fields.Many2one('account.tax', string="Tax allowance")
    deduction_tax_percent = fields.Float(
        compute='_compute_deduction_tax', store=True)
    deduction_tax_amount = fields.Monetary(
        compute='_compute_deduction_tax',
        string="Tax allowance Amount", store=True)
    # for journal item
    entry_deduction_tax_id = fields.Many2one(
        'account.tax', string="Deduction/Withholding Tax")
