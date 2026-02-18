""" Initialize  hr.job """

from odoo import fields, models


# pylint: disable=no-member,protected-access
class HrJob(models.Model):
    """
        inherit hr.job:
    """
    _inherit = 'hr.job'

    performance_template_ids = fields.One2many(
        comodel_name='hr.performance.template',
        inverse_name='job_id',
    )
