""" Company """

from odoo import fields, models


class ResCompany(models.Model):
    """ inherit Company to add configuration """
    _inherit = 'res.company'

    employee_document_expiry = fields.Integer(
        default='30'
    )
