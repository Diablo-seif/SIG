
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    integration_token = fields.Char()
    refresh_token = fields.Char(copy=False)
