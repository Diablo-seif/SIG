""" Initialize Res Config Settings """

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    """
        Inherit res.config.setting
    """
    _inherit = 'res.config.settings'

    journal_entry_signature = fields.Boolean(
        related='company_id.journal_entry_signature',
        readonly=False
    )
