""" Initialize Res Config Settings """

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    """ Inherit res.config.setting model to add  configuration"""
    _inherit = 'res.config.settings'

    payment_request_responsible_id = fields.Many2one(
        related='company_id.payment_request_responsible_id', readonly=False)
