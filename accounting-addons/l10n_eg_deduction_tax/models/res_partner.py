""" Inherited res partner"""

from odoo import models, fields


class ResPartner(models.Model):
    """inherit res.partner to add deduction tax details"""
    _inherit = 'res.partner'

    deduction_tax_exemption_status = fields.Selection([
        ('not_exempt', 'Not Exempt'),
        ('advanced', 'Advanced Payment'), ('exempt', 'Exempt')])
    exemption_expire_date = fields.Date()
