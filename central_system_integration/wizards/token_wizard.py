
from odoo import models, fields

class TokenWizard(models.TransientModel):
    _name = 'token.wizard'
    _description = 'Token Wizard'

    token = fields.Char(readonly=True)