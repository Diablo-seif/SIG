""" inherit res.company to add income tax entry accounts """

from odoo import fields, models


class ResCompany(models.Model):
    """
    inherit res.company to add income tax entry accounts
    """
    _inherit = 'res.company'

    income_tax_entry_from_account_id = fields.Many2one("account.account")
    income_tax_rounding = fields.Selection([
        ('ceil', 'Ceiling'), ('none', 'None'), ('floor', 'Floor')])
    income_tax_rounding_base = fields.Integer()
    base_after_losses_rounding = fields.Selection([
        ('ceil', 'Ceiling'), ('none', 'None'), ('floor', 'Floor')])
    base_after_losses_rounding_base = fields.Integer()
