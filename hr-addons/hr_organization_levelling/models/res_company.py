""" inherit res.company to add levelling configuration """

from odoo import fields, models


class ResCompany(models.Model):
    """ `organization_levelling` added to carry configuration value """
    _inherit = 'res.company'

    organization_levelling = fields.Integer(
        default=1
    )
