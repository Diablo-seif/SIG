""" model to carry employee documents """

from odoo import fields, models


class HrEmployeeDocuments(models.Model):
    """ Employee Documents """
    _name = 'hr.employee.documents'
    _description = 'HR Employee Documents'

    name = fields.Char(
        required=True,
        translate=True
    )
    has_expiration = fields.Boolean(
        help='Document must be defined with expiry date'
    )
    require_original = fields.Boolean(
        help='Document must be original'
    )
    default_document = fields.Boolean(
        default=True,
        help='Will be listed as default documents when creating new employee'
    )
