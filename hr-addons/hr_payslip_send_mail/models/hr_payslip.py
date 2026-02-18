""" Update object hr.payslip """

from odoo import api, fields, models


# pylint: disable=no-member,attribute-string-redundant
class HrPayslip(models.Model):
    """ Update object hr.payslip """
    _inherit = ["hr.payslip", "mail.thread"]
    _name = "hr.payslip"

    def schedule_compute_sheet(self):
        """
        Schedule Compute Sheet.
        """
        self.compute_sheet()

    def schedule_payslip_done(self):
        """
        Schedule payslip_done.
        """
        self.action_payslip_done()

    def schedule_send_payslip(self):
        """
        Schedule send Payslip.
        """
        self.action_payslip_send_only()

    def action_payslip_send_only(self):
        """
        Function Send Mail Without Wizard
        :return:
        """
        template = self.env.ref('hr_payslip_send_mail.'
                                'email_template_edi_payslip')
        for rec in self:
            if not rec.mark_payslip_as_sent and template:
                template.send_mail(rec.id, force_send=False)
                rec.mark_payslip_as_sent = True

    def action_payslip_send(self):
        """
        This function open a Wizard to send Mail
        """
        self.ensure_one()
        ir_model = self.env['ir.model.data']
        template_id = ir_model.get_object_reference(
            'hr_payslip_send_mail', 'email_template_edi_payslip')[1]
        compose_form_id = ir_model.get_object_reference(
            'mail', 'email_compose_message_wizard_form')[1]
        ctx = {
            'default_model': 'hr.payslip',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_payslip_as_sent': True,
            'custom_layout': "hr_payslip_send_mail."
                             "mail_template_data_notification_email_payslip",
            'proforma': self.env.context.get('proforma', False),
            'force_email': True
        }
        if template_id:
            ctx.update(default_template_id=template_id)
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    @api.depends('uuid_compute_job')
    def _compute_compute_job_id(self):
        """
        Compute compute_job_id.
        """
        for rec in self:
            c_job_id = self.env['queue.job'].search([
                ('model_name', '=', 'hr.payslip'),
                ('method_name', '=', 'schedule_compute_sheet'),
                ('uuid', '=', rec.uuid_compute_job),
            ], limit=1)
            if c_job_id:
                rec.compute_job_id = c_job_id.id

    @api.depends('uuid_confirm_job')
    def _compute_confirm_job_id(self):
        """
        Compute confirm_job_id.
        """
        for rec in self:
            cn_job_id = self.env['queue.job'].search([
                ('model_name', '=', 'hr.payslip'),
                ('method_name', '=', 'schedule_payslip_done'),
                ('uuid', '=', rec.uuid_confirm_job),
            ], limit=1)
            if cn_job_id:
                rec.confirm_job_id = cn_job_id.id

    def _compute_send_job_id(self):
        """
        Compute send_job_id.
        """
        domain = [
            ('model_name', '=', 'hr.payslip'),
            ('method_name', '=', 'schedule_send_payslip'),
        ]
        queue_jobs = self.env['queue.job'].search(domain)
        for rec in self:
            # pylint: disable=cell-var-from-loop
            ids = [rec.id]
            s_job_id = queue_jobs.filtered(lambda qjs: qjs.record_ids == ids)
            if s_job_id:
                rec.send_job_id = s_job_id[0].id

    # pylint: disable=unused-argument
    def _search_job(self, operator, value):
        """
        Override Search Job.
        :param operator:
        :param value:
        :return: domain
        """
        job_ids = False
        job_id = False
        list_ids = []
        if isinstance(value, int):
            job_id = self.env['queue.job'].browse(value)
        elif isinstance(value, list):
            job_ids = self.env['queue.job'].browse(value)
        if job_id and job_id.record_ids:
            list_ids = job_id.record_ids
        if job_ids:
            for job_id in job_ids:
                if job_id.record_ids:
                    list_ids += job_id.record_ids
        if list_ids:
            return [('id', 'in', list_ids)]
        return []

    @api.depends('progress')
    def _compute_state(self):
        """
        Compute State.
        """
        for rec in self:
            if rec.progress == -1:
                rec.state = 'draft'
            elif rec.progress == 100:
                rec.state = "done"
            else:
                rec.state = "in_progress"

    mark_payslip_as_sent = fields.Boolean(string="Email has been sent")
    uuid_compute_job = fields.Char()
    uuid_confirm_job = fields.Char()
    compute_job_id = fields.Many2one(
        'queue.job', compute='_compute_compute_job_id', compute_sudo=True,
        store=True, search='_search_job'
    )
    compute_status = fields.Selection(
        related="compute_job_id.state", store=True, string='Compute'
    )
    confirm_job_id = fields.Many2one(
        'queue.job', compute='_compute_confirm_job_id', compute_sudo=True,
        store=True, search='_search_job'
    )
    confirm_status = fields.Selection(
        related='confirm_job_id.state', store=True, string='Confirm'
    )
    send_job_id = fields.Many2one(
        'queue.job', compute='_compute_send_job_id', compute_sudo=True,
        store=True, search='_search_job'
    )
    send_status = fields.Selection(
        related="send_job_id.state", store=True, string='Send'
    )
