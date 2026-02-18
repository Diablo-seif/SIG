""" inherit res.config.settings to add employee documents expiration """

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    """ Inherit res.config.settings to add  employee documents expiration """
    _inherit = 'res.config.settings'

    employee_document_expiry = fields.Integer(
        related='company_id.employee_document_expiry',
        readonly=0,
        default='30',
        help='When to schedule activity before '
             'employee documents be expired'
    )
