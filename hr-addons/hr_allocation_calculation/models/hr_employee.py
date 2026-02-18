""" HR Employee """
from odoo import fields, models


class HrEmployee(models.Model):
    """ inherit HR Employee """
    _inherit = 'hr.employee'

    allocation_tag_id = fields.Many2one(
        'hr.allocation.tag', groups="hr.group_hr_user"
    )
