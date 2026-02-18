"""init Settlement Deduction Tax wizard"""

from odoo import _, models, fields
from odoo.exceptions import UserError


class SettlementDeductionTaxWizard(models.TransientModel):
    """
    Settlement Deduction Tax Wizard
    """
    _name = "settlement.deduction.tax.wizard"
    _description = "Settlement Deduction Tax Wizard"

    def _get_default_journal(self):
        """ get default journal """
        return self.env['account.journal'].search([
            ('company_id', '=', self.env.company.id),
            ('type', '=', 'purchase')], limit=1)

    def create_bill(self):
        """ create Settlement Deduction Tax """
        active_model = self.env.context.get('active_model')
        active_ids = self.env.context.get('active_ids')
        if not active_ids or not active_model:
            return
        lines = self.env[active_model].browse(active_ids)
        currency_ids = lines.mapped('currency_id')
        if len(currency_ids) > 1:
            raise UserError(_("Can't creat bill with different currencies"))
        move = self.env['account.move'].create({
            'move_type': 'in_invoice', 'partner_id': self.partner_id.id,
            'invoice_date': self.bill_date, 'currency_id': currency_ids[0].id,
            'journal_id': self.journal_id.id,
            'invoice_line_ids': [
                (0, 0, {
                    'name': "%s - %s" % (
                        line.payment_id.name, line.vendor_name),
                    'product_id': self.product_id.id, 'tax_ids': False,
                    'quantity': 1, 'price_unit': line.tax_amount,
                    'account_id': line.deduction_tax_id.mapped(
                        'invoice_repartition_line_ids.account_id').id,
                }) for line in lines]
        })
        return {
            'type': 'ir.actions.act_window', 'res_model': 'account.move',
            'view_mode': 'form', 'name': _('Settlement Deduction Tax'),
            'res_id': move.id, 'context': {'create': False}}

    partner_id = fields.Many2one('res.partner', required=True)
    product_id = fields.Many2one('product.product')
    bill_date = fields.Date(required=True)
    journal_id = fields.Many2one(
        'account.journal', required=True, default=_get_default_journal)
