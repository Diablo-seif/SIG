""" Inherit hr.department """

from odoo import fields, models


class HrDepartment(models.Model):
    """
        inherit hr.department:
    """
    _inherit = 'hr.department'

    type = fields.Selection([
        ('external', 'External'),
        ('internal', 'Internal')
    ])

