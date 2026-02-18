""" HR Job """

from odoo import fields, models


class HrJob(models.Model):
    """ inherit HR Job to link with courses """
    _inherit = 'hr.job'

    course_ids = fields.Many2many(
        'hr.course',
        'course_job_ref'
    )
