
from odoo import fields, models
import secrets


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    integration_token = fields.Char(
        related='company_id.integration_token',
        readonly=False
    )

    def action_generate_token(self):
        token = secrets.token_urlsafe(32)

        wizard = self.env['token.wizard'].create({
            'token': token
        })
        self.company_id.integration_token = token

        return {
            'name': 'Generated Token',
            'type': 'ir.actions.act_window',
            'res_model': 'token.wizard',
            'view_mode': 'form',
            'res_id': wizard.id,
            'target': 'new',
        }
        