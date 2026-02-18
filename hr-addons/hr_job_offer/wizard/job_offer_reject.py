""" Job Offer Reject """
from odoo import fields, models


class JobOfferReject(models.TransientModel):
    """ Job Offer Reject """
    _name = 'job.offer.reject'
    _description = 'Job Offer Reject'

    action_reason_ids = fields.Many2many(
        'action.reason', required=True, string='Rejection Reason'
    )
    note = fields.Text()

    def action_reject(self):
        """ Action Reject """
        self.ensure_one()
        for rec in self.env['hr.job.offer'].browse(
                self.env.context.get('active_ids')):
            rec.action_reason_ids = self.action_reason_ids
            rec.note = self.note
            rec.state = 'rejected'
