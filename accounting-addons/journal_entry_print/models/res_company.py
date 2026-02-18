""" Initialize Res Company """

from odoo import fields, models


class ResCompany(models.Model):
    """
        Inherit Res Company:
    """
    _inherit = 'res.company'

    journal_entry_signature = fields.Boolean()
