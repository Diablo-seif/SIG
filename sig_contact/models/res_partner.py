""" Initialize Res Partner """

from odoo import fields, models


class ResPartner(models.Model):
    """
        Inherit Res Partner:
         -
    """
    _inherit = 'res.partner'

    is_shareholder = fields.Boolean()
    is_secret = fields.Boolean()
    is_vendor = fields.Boolean()
    is_customer = fields.Boolean()
    is_vip = fields.Boolean()

    shareholder_account_payable_id = fields.Many2one('account.account',         
        domain="['|', ('account_type', '=', 'liability_payable'), ('account_type', '=', 'asset_receivable'), ('deprecated', '=', False), ('company_id', '=', current_company_id)]",
    )
    shareholder_account_receivable_id = fields.Many2one('account.account',
        domain="['|', ('account_type', '=', 'liability_payable'), ('account_type', '=', 'asset_receivable'), ('deprecated', '=', False), ('company_id', '=', current_company_id)]",
    )
