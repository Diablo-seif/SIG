""" HR Course Type """

from odoo import fields, models


class HrCourseType(models.Model):
    """HR Course Type """

    _name = "hr.course.type"

    name = fields.Char(
        required=True
    )
