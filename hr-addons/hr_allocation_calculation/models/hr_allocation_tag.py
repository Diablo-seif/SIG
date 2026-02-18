""" HR Allocation Tag """
from odoo import _, fields, models


class HrAllocationTag(models.Model):
    """ HR Allocation Tag """
    _name = 'hr.allocation.tag'
    _description = 'Allocation Tag'
    _sql_constraints = [
        ('unique_name', 'UNIQUE(name)', _('Name must be unique')),
    ]
    name = fields.Char(required=True)
