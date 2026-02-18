""" This Module For Update Employee """

from datetime import date

from odoo import fields, models


class HrEmployee(models.Model):
    """  Add Employee Age"""
    _inherit = 'hr.employee'

    def _compute_age(self):
        """compute age."""
        today = date.today()
        for rec in self:
            age = 0
            if rec.birthday:
                age = int((today - rec.birthday).days / 365)
            rec.age = age

    age = fields.Integer(compute=_compute_age, groups="hr.group_hr_user")
