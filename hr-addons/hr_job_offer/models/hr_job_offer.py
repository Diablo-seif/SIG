""" Job Offer """

from odoo import _, api, fields, models


class HrJobOffer(models.Model):
    """ Job Offer """
    _name = 'hr.job.offer'
    _description = 'Job Offer'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        default='New'
    )
    applicant_id = fields.Many2one(
        'hr.applicant',
        required=True
    )
    validity_date = fields.Date(
        required=True,
        default=fields.Date.today()
    )
    generate_date = fields.Datetime(
        readonly=True
    )
    state = fields.Selection(
        [('sent', 'Offer Sent'),
         ('approved', 'Approved'),
         ('rejected', 'Rejected')],
        string='Status',
        readonly=True,
        copy=False,
        index=True,
        default='sent'
    )
    action_reason_ids = fields.Many2many(
        'action.reason',
        readonly=True,
        string='Rejection Reason'
    )
    note = fields.Text(
        tracking=True
    )

    @api.model
    def create(self, vals_list):
        """ Override create method to sequence name """
        if vals_list.get('name', 'New') == 'New':
            vals_list['name'] = self.env['ir.sequence'].next_by_code(
                'job.offer') or '/'
        return super().create(vals_list)

    # pylint: disable=no-member
    def action_job_offer_send(self):
        """
            Opens a wizard to compose an email, with
            relevant mail template loaded by default
        """
        self.ensure_one()
        template = self.env.ref(
            'hr_job_offer.job_offer_mail_template_id', raise_if_not_found=False)
        ctx = {
            'default_model': self._name,
            'default_res_id': self.id,
            'default_use_template': bool(template),
            'default_template_id': template.id,
            'default_composition_mode': 'comment',
            'force_email': True,
            'model_description': _('Job Offer'),
        }
        self.generate_date = fields.Datetime.now()
        self.write({'state': 'sent'})
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }

    def report_print(self):
        """ Print job offer """
        self.ensure_one()
        report = self.env.ref(
            'hr_job_offer.job_offer_report').report_action(self)
        self.generate_date = fields.Datetime.now()
        return report

    def action_approve(self):
        """ Approved Offer"""
        self.write({'state': 'approved'})
