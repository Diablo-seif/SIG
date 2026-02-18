""" HR employee """
from odoo import fields, models


class HrEmployee(models.Model):
    """ HR Employee """
    _inherit = 'hr.employee'

    contract_type_id = fields.Many2one(
        'hr.contract.type', groups="hr.group_hr_user"
    )
