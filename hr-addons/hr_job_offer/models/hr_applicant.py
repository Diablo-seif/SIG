""" Inherit HR Applicant to add  job offer"""

from odoo import SUPERUSER_ID, _, fields, models
from odoo.exceptions import ValidationError


class HrApplicant(models.Model):
    """ inherit HR Applicant to add more needed fields """
    _inherit = 'hr.applicant'

    country_id = fields.Many2one('res.country', string='Nationality')
    address_id = fields.Many2one(
        'res.partner', related='job_id.address_id', readonly=1)
    resource_calendar_id = fields.Many2one(
        'resource.calendar', string='Working Days',
        default=lambda self: self.env.company.resource_calendar_id.id
    )
    job_offer_ids = fields.One2many('hr.job.offer', 'applicant_id')
    sign_signature = fields.Binary()

    # pylint: disable=protected-access
    def action_approve(self):
        """ Approve application and add signature """
        for application in self:
            user_id = application.user_id.id or SUPERUSER_ID
            if not self.env.user.sign_signature:
                raise ValidationError(_('You have to contact administrator '
                                        'to add your signature'))
            application.sign_signature = self.env.user.sign_signature
            application._activity_schedule_with_view(
                'mail.mail_activity_data_todo',
                views_or_xmlid='hr_recruitment.crm_case_tree_view_job',
                user_id=user_id,
                summary="Application approved"
            )

    def action_view_job_offers(self):
        """ Smart button to run action """
        job_offers = self.mapped('job_offer_ids')
        action = self.env.ref(
            'hr_job_offer.view_hr_job_offer_action').sudo().read()[0]
        action['domain'] = [('id', 'in', job_offers.ids)]
        return action
