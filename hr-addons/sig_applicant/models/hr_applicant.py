""" Inherit hr.applicant """

from odoo import fields, models


class HrApplicant(models.Model):
    """
        inherit hr.applicant:
    """
    _inherit = 'hr.applicant'

    image = fields.Binary()
    referred_id = fields.Many2one('res.partner', domain="[('is_vip', '=', True)]")
