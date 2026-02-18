""" Res Config Settings """

from odoo import fields, models


class PayrollConfigSettings(models.TransientModel):
    """ Inherit res.config.setting model to add Payroll configuration"""
    _inherit = 'res.config.settings'

    month_start = fields.Selection(
        related='company_id.month_start',
        readonly=False,
        required=True
    )
