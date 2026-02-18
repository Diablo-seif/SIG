""" HR Course """

from odoo import fields, models


class HrCourse(models.Model):
    """ HR Course """
    _name = "hr.course"
    _description = 'Training Course'

    name = fields.Char(
        required=True
    )
    description = fields.Text()
    job_ids = fields.Many2many(
        'hr.job',
        'course_job_ref'
    )
    active = fields.Boolean(
        default=True,
        help="If the active field is set to false, it will"
             "allow you to hide the Course without removing it."
    )
    course_type_id = fields.Many2one(
        "hr.course.type"
    )
    provider_ids = fields.One2many(
        "hr.course.provider.line",
        "course_id"
    )
