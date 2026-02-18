""" This Module For Update Employee """

from odoo import fields, models


class HrEmployee(models.Model):
    """  Add Employee Military data """
    _inherit = 'hr.employee'

    military_status = fields.Selection(
        [('served', 'Served'),
         ('postponed', 'Postponed'),
         ('exempted', 'Exempted')], groups="hr.group_hr_user",
    )
