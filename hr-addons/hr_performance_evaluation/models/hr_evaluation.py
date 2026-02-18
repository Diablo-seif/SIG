""" Initialize hr.evaluation """

from odoo import _, api, fields, models
from odoo.exceptions import UserError


# pylint: disable=no-member,protected-access
class HrEvaluation(models.Model):
    """
        init hr.evaluation:
    """
    _name = 'hr.evaluation'
    _description = 'HR Evaluation'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _check_company_auto = True

    name = fields.Char(
        required=True,
        copy=False,
        default='/',
        tracking=True,
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        default=lambda self: self.env.company,
        tracking=True,
    )
    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        required=True,
        check_company=True,
        domain="[('job_id', '!=', False), "
               "('job_id.performance_template_ids', '!=', False), "
               "('job_id.performance_template_ids.active', '=', True),"
               " '|', ('company_id', '=', False),"
               " ('company_id', '=', company_id)]",
        index=True,
        tracking=True,
        ondelete='restrict',
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Related Partner',
        related_sudo=True,
        related='employee_id.user_id.partner_id',
        store=True,
        compute_sudo=True,
    )
    user_id = fields.Many2one(
        comodel_name='res.users',
        related='employee_id.user_id',
        related_sudo=True,
        compute_sudo=True,
        store=True,
        default=lambda self: self.env.uid,
        readonly=True,
        ondelete='restrict',
    )
    job_id = fields.Many2one(
        related='employee_id.job_id',
        related_sudo=True,
        store=True,
    )
    manager_id = fields.Many2one(
        related='employee_id.parent_id',
        related_sudo=True,
        store=True,
    )
    performance_template_id = fields.Many2one(
        comodel_name='hr.performance.template',
        check_company=True,
        domain="[('job_id', '=', job_id),"
               " '|', ('company_id', '=', False),"
               " ('company_id', '=', company_id)]",
        tracking=True,
        ondelete='restrict',
    )
    period_id = fields.Many2one(
        comodel_name='hr.evaluation.period',
        check_company=True,
        domain="['|', ('company_id', '=', False),"
               " ('company_id', '=', company_id)]",
        tracking=True,
        ondelete='restrict',
    )
    start_date = fields.Date(
        compute='_compute_date_start_end',
        store=True,
        tracking=True,
    )
    end_date = fields.Date(
        compute='_compute_date_start_end',
        store=True,
        tracking=True,
    )
    deadline_date = fields.Date(
        string='Deadline',
        tracking=True,
    )
    state = fields.Selection(
        string='Status',
        selection=[('draft', 'Draft'),
                   ('send_to_manager', 'Sent To Manager'),
                   ('done', 'Done'),
                   ('cancel', 'Cancelled'),
                   ],
        required=True,
        default='draft',
        copy=False,
        tracking=True,
        index=True,
    )
    performance_line_ids = fields.One2many(
        comodel_name='hr.evaluation.performance.line',
        inverse_name='evaluation_id',
        copy=True,
        string='Key Performance Area Questions',
    )
    employee_done_evaluation = fields.Boolean()
    manager_done_evaluation = fields.Boolean()
    performance_score_percentage = fields.Float(
        compute='_compute_performance_score_percentage',
        store=True,
    )
    performance_score_scale_id = fields.Many2one(
        comodel_name='hr.performance.score.scale',
        compute='_compute_performance_score_scale',
        store=True,
    )
    total_objective_score_percentage = fields.Float(
        compute='_compute_score_percentage',
        store=True,
    )
    evaluation_percentage = fields.Float(
        compute='_compute_score_percentage',
        store=True,
    )

    @api.depends('performance_score_percentage',
                 'performance_template_id.objective_percentage')
    def _compute_score_percentage(self):
        """ Compute _compute_score_percentage value """
        for rec in self:
            total_objective_score_percentage = rec.performance_score_percentage * rec.performance_template_id.objective_percentage
            rec.evaluation_percentage = total_objective_score_percentage
            rec.total_objective_score_percentage = total_objective_score_percentage

    @api.depends('performance_score_percentage', 'company_id')
    def _compute_performance_score_scale(self):
        """
        get score scale based on percentage
        """
        for record in self:
            score_scale = self.env['hr.performance.score.scale'].search([
                ('company_id', '=', record.company_id.id),
                ('score_from', '<', record.evaluation_percentage),
                ('score_to', '>=', record.evaluation_percentage),
            ], limit=1)
            record.performance_score_scale_id = score_scale

    @api.depends('performance_line_ids', 'performance_line_ids.display_type',
                 'performance_line_ids.final_score_percentage')
    def _compute_performance_score_percentage(self):
        """
        get percentage based on number of lines and manager score
        """
        for record in self:
            record.performance_score_percentage = \
                sum(record.performance_line_ids.filtered(
                    lambda line: not line.display_type
                ).mapped('final_score_percentage'))

    @api.onchange('employee_id')
    def _onchange_employee(self):
        """
        update template from employee job position
        """
        self.performance_template_id = \
            self.employee_id.job_id.performance_template_ids

    @api.depends('period_id')
    def _compute_date_start_end(self):
        """
        update start & end data based on period
        """
        for record in self:
            record.start_date = \
                record.period_id.start_date if record.period_id else False
            record.end_date = \
                record.period_id.end_date if record.period_id else False

    @api.onchange('performance_template_id')
    def _onchange_performance_template(self):
        """
        update lines based on template
        """
        objective_line = self.performance_template_id.objective_line_ids
        self.performance_line_ids = \
            [(5, 0, 0)] + objective_line.mapped(lambda r: (0, 0, {
                'display_type': r.display_type,
                'name': r.name,
                'sequence': r.sequence,
                'description': r.description,
                'hint': r.hint,
                'weightage': r.weightage,
            }))

    @api.model
    def create(self, vals):
        company_id = vals.get('company_id',
                              self.default_get(['company_id'])['company_id'])
        self_comp = self.with_company(company_id)
        if vals.get('name', '/') == '/':
            vals['name'] = self_comp.env['ir.sequence']. \
                               next_by_code('hr.employee.evaluation') or '/'
        return super(HrEvaluation, self_comp).create(vals)

    def unlink(self):
        for record in self:
            if record.state not in ('draft', 'cancel'):
                raise UserError(
                    _('You can not delete evaluation.'
                      ' You must first cancel it.'))
        return super(HrEvaluation, self).unlink()

    def _notify_get_groups(self, msg_vals=None):
        """ Give access button to users and portal customer as portal is integrated
        in sale. Customer and portal group have probably no right to see
        the document so they don't have the access button. """
        groups = super(HrEvaluation, self)._notify_get_groups(msg_vals=msg_vals)
        self.ensure_one()
        if self.state not in ('draft', 'cancel'):
            for group_name, group_method, group_data in groups:
                if group_name != 'portal':
                    group_data['has_button_access'] = True
        return groups

    def action_cancel(self):
        """
        set cancel
        """
        self.write({
            'state': 'cancel',
        })

    def action_send_to_manager(self):
        """
        update status and send message to manager
        """
        for record in self:
            if record.deadline_date and \
                    record.deadline_date < fields.Date.today():
                raise UserError(_('Cannot perform any action after deadline!'))
            record.state = 'send_to_manager'
            manager = record.employee_id.parent_id
            if manager and manager.user_id:
                body = _('%s evaluation is ready to review!') \
                       % record.employee_id.display_name
                if record.deadline_date:
                    body += _('Deadline date is %s') % record.deadline_date
                record.message_post(
                    body=body,
                    partner_ids=manager.user_id.partner_id.ids,
                    subject=
                    _('%s Evaluation') % record.employee_id.display_name,
                    subtype_xmlid='mail.mt_comment',
                )

    def action_employee_done_evaluation(self):
        """
        mark evaluation as added by employee
        """
        for record in self:
            manager = record.employee_id.parent_id
            if manager and manager.user_id:
                # @formatter:off
                record.message_post(
                    body=_('Employee %s finish his evaluation.')
                         % record.employee_id.display_name,
                    partner_ids=manager.user_id.partner_id.ids,
                    subtype_xmlid='mail.mt_comment',
                )
                # @formatter:on
            record.employee_done_evaluation = True
        self.action_send_to_manager()

    def action_submit(self):
        """ Action Submit """
        for rec in self:
            rec.state = 'send_to_manager'

    def action_done(self):
        """
        update status and send message to employee and manager
        """
        if any(record.state != 'send_to_manager' for record in self):
            raise UserError(_('Evaluation must be in send to manager '
                              'to mark done'))
        for record in self:
            partners = self.env['res.partner']
            if record.user_id:
                partners |= record.user_id.partner_id
            if record.employee_id.parent_id \
                    and record.employee_id.parent_id.user_id:
                partners |= record.employee_id.parent_id.user_id.partner_id
            if partners:
                record.message_post(
                    body=_('Evaluation %s is done.') % record.display_name,
                    partner_ids=partners.ids,
                    subtype_xmlid='mail.mt_comment',
                )
            record.state = 'done'

    def action_reset_draft(self):
        """
        reset evaluation to draft
        """
        if any(record.state != 'cancel' for record in self):
            raise UserError(_('Evaluation must be in cancel '
                              'to convert to draft'))
        self.write({
            'state': 'draft',
            'employee_done_evaluation': False,
            'manager_done_evaluation': False,
        })

    def _get_portal_return_action(self):
        """ Return the action used to display evaluations when returning
        from portal. """
        self.ensure_one()
        return self.env.ref(
            'hr_performance_evaluation.hr_evaluation_all_action')
