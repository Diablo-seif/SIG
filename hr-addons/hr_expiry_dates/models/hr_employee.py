""" update object employee """

from odoo import models, fields


class HrEmployee(models.Model):
    """  Add Branches and Working schedule to Employee """
    _inherit = 'hr.employee'

    identification_expiry_date = fields.Date(groups="hr.group_hr_user")
    passport_expiry_date = fields.Date(groups="hr.group_hr_user")
