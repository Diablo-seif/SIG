""" Add job description HR Job  """

from odoo import api, fields, models


class HrJob(models.Model):
    """ Add job description template """
    _inherit = 'hr.job'

    job_description_template_id = fields.Many2one(
        'hr.job.description.template'
    )
    website_description = fields.Html(
        'Job description',
        compute='_compute_job_description',
        store=True,
        readonly=False,
        default=''
    )

    @api.depends('job_description_template_id')
    def _compute_job_description(self):
        """ get job description from template """
        for rec in self:
            rec.website_description = \
                rec.job_description_template_id.job_description
