""" Add job description HR Job  """

from odoo import fields, models
from odoo.tools.translate import html_translate


# pylint:disable=protected-access
class HrJobDescriptionTemplate(models.Model):
    """ HR Job Description Template """
    _name = 'hr.job.description.template'
    _description = 'Job Description Templates'

    def _get_default_website_description(self):
        """ get default template """
        default_description = self.env['ir.model.data'].xmlid_to_object(
            'website_hr_recruitment.default_website_description')
        return default_description._render() if default_description else ''

    name = fields.Char(
        required=True,
        translate=True
    )
    job_description = fields.Html(
        required=True,
        translate=html_translate,
        sanitize_attributes=False,
        default=_get_default_website_description,
        prefetch=False
    )
