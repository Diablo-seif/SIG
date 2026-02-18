""" Initialize Account Payment """

from odoo import fields, models, api


class AccountPayment(models.Model):
    """
        Inherit Account Payment:
         -
    """
    _inherit = 'account.payment'

    is_shareholder = fields.Boolean()
    shareholder_id = fields.Many2one('res.partner',
                    domain="[('is_shareholder', '=', True)]")
    
    
    @api.onchange('shareholder_id')
    def _onchange_(self):
        if self.is_shareholder:
            self.partner_id = self.shareholder_id
            
    
    @api.depends('journal_id', 'partner_id', 'partner_type', 'is_internal_transfer', 'destination_journal_id')
    def _compute_destination_account_id(self):
        self.destination_account_id = False
        for pay in self:
            if pay.is_internal_transfer:
                pay.destination_account_id = pay.destination_journal_id.company_id.transfer_account_id
            elif pay.partner_type == 'customer':
                # Receive money from invoice or send money to refund it.
                if pay.partner_id:
                    if pay.is_shareholder:
                        pay.destination_account_id = pay.partner_id.with_company(pay.company_id).shareholder_account_receivable_id
                    else:    
                        pay.destination_account_id = pay.partner_id.with_company(pay.company_id).property_account_receivable_id
                else:
                    pay.destination_account_id = self.env['account.account'].search([
                        ('company_id', '=', pay.company_id.id),
                        ('account_type', '=', 'asset_receivable'),
                        ('deprecated', '=', False),
                    ], limit=1)
            elif pay.partner_type == 'supplier':
                # Send money to pay a bill or receive money to refund it.
                if pay.partner_id:
                    if pay.is_shareholder:
                        pay.destination_account_id = pay.partner_id.with_company(pay.company_id).shareholder_account_payable_id
                    else:    
                        pay.destination_account_id = pay.partner_id.with_company(pay.company_id).property_account_payable_id
                        
                else:
                    pay.destination_account_id = self.env['account.account'].search([
                        ('company_id', '=', pay.company_id.id),
                        ('account_type', '=', 'liability_payable'),
                        ('deprecated', '=', False),
                    ], limit=1)
    
