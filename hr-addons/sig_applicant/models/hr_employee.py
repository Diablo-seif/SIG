from odoo import fields, models, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    referred_id = fields.Many2one('res.partner', domain="[('is_vip', '=', True)]", compute='_compute_referred_id',
                                  readonly=False, store=True)
    source_id = fields.Many2one('utm.source', compute='_compute_source_id', readonly=False, store=True)

    @api.depends('applicant_id.referred_id')
    def _compute_referred_id(self):
        for record in self:
            if len(record.applicant_id) > 0:
                application = record.applicant_id[0]
                record.referred_id = application.referred_id
            else:
                record.referred_id = False

    @api.depends('applicant_id.source_id')
    def _compute_source_id(self):
        for record in self:
            if len(record.applicant_id) > 0:
                application = record.applicant_id[0]
                record.source_id = application.source_id
            else:
                record.source_id = False
