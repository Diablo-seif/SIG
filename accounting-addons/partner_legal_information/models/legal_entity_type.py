"""Define Legal Entity Type For Organization"""

from odoo import models, fields


class LegalEntityType(models.Model):
    """ init legal entity type"""
    _name = 'legal.entity.type'
    _description = 'Legal Entity Type'

    name = fields.Char(
        required=True,
        translate=True,
    )
    active = fields.Boolean(
        default=True,
    )
