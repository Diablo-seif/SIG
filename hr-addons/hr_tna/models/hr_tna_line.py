""" Department Training Needs Assessment """
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


# pylint: disable=protected-access,no-member
class HrTnaLine(models.Model):
    """ Department Training Needs Assessment """
    _name = 'hr.tna.line'
    _description = 'Department Training Needs Assessment'
    _rec_name = 'department_id'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    _sql_constraints = [
        ('unique_tna_line',
         'UNIQUE(tna_id,department_id,job_id,course_id)',
         _("TNA line can't be duplicated")),
        ('check_number_of_participants',
         'CHECK(no_of_participants>=0)',
         _('No Of Participants must be positive')),
        ('check_approved_no_of_participants',
         'CHECK(approved_no_of_participants>=0)',
         _('Approved No Of Participants must be positive')),
    ]

    @api.model
    def _get_department_domain(self):
        if self.user_has_groups('hr_tna.group_tna_manager'):
            return []
        return [('manager_id', '=', self.env.user.employee_id.id)]

    job_id = fields.Many2one(
        'hr.job', domain="[('department_id', '=', department_id)]",
        required=True
    )
    department_id = fields.Many2one(
        'hr.department', domain=lambda self: self._get_department_domain(),
        default=lambda self: self.env['hr.department'].search(
            [('manager_id', '=', self.env.user.employee_id.id)], limit=1).id,
        required=True
    )
    course_id = fields.Many2one(
        'hr.course', required=True, domain="[('job_ids.id', '=', job_id)]"
    )
    provider_id = fields.Many2one(
        'hr.course.provider.line', domain="[('course_id', '=', course_id)]",
    )
    provider_type = fields.Selection(
        related='provider_id.provider_type', store=True
    )
    no_of_participants = fields.Integer(tracking=True)
    approved_no_of_participants = fields.Integer(tracking=True)
    unit_budget = fields.Monetary(
        currency_field='currency_id', compute='_compute_unit_budget',
        store=True, readonly=False
    )
    planned_budget = fields.Monetary(
        currency_field='currency_id', compute='_compute_budget', store=True
    )
    approved_budget = fields.Monetary(
        currency_field='currency_id', compute='_compute_budget', store=True
    )

    note = fields.Text(tracking=True)
    currency_id = fields.Many2one(
        'res.currency', default=lambda self: self.env.company.currency_id.id
    )
    tna_course_ids = fields.One2many(
        'hr.tna.courses', 'tna_line_id', string='TNA Courses'
    )
    tna_id = fields.Many2one('hr.tna', ondelete='cascade')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('budgeted', 'Budgeted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], default='draft', readonly=True, tracking=True)

    @api.constrains('tna_course_ids')
    def _check_tna_course_ids(self):
        """ Validate tna_course_ids """
        for rec in self:
            if len(rec.tna_course_ids) > rec.approved_no_of_participants:
                raise ValidationError(
                    _('Number of employees can\'t exceed %s') %
                    rec.approved_no_of_participants
                )

    # pylint: disable=cell-var-from-loop
    @api.constrains('no_of_participants', 'job_id')
    def _check_no_of_participants(self):
        """ Validate no_of_participants """
        for rec in self:
            current_employees = rec.job_id.no_of_employee
            planned_employees = 0
            if 'manpower_line_ids' in rec.job_id.fields_get_keys():
                # @formatter:off
                planned_employees = sum(rec.job_id.manpower_line_ids.filtered(
                    lambda r: r.state == 'approved' and
                    r.reason == 'new_hire' and
                    r.start_date >= rec.tna_id.date_from and
                    r.start_date <= rec.tna_id.date_to
                ).mapped('approved_no_of_position'))
            total_employees = current_employees + planned_employees
            if rec.no_of_participants > total_employees:
                raise ValidationError(
                    _('Number of participants can\'t exceed '
                      '%(employee_number)s for %(job_name)s job position') % {
                          "employee_number": total_employees,
                          "job_name": rec.job_id.name
                      }
                )

    @api.depends(
        'no_of_participants', 'approved_no_of_participants', 'unit_budget'
    )
    def _compute_budget(self):
        """ Compute budget value """
        for rec in self:
            rec.planned_budget = rec.no_of_participants * rec.unit_budget
            rec.approved_budget = \
                rec.approved_no_of_participants * rec.unit_budget

    @api.depends('provider_id', 'tna_id.tna_line_ids.provider_id')
    def _compute_unit_budget(self):
        """ Get unit budget from selected provider to ensure that
        total budget exceeded min budget to provider """
        for rec in self:
            # @formatter:off
            same_lines = rec.tna_id.tna_line_ids.filtered(
                lambda r: r.course_id == rec.course_id and
                r.provider_id == rec.provider_id
            )
            course_no_of_participants = sum(same_lines.mapped(
                'no_of_participants'))
            each_cost = rec.provider_id.cost_per_participant

            if course_no_of_participants < \
                    rec.provider_id.minimum_no_of_participants:
                min_cost = rec.provider_id.cost_per_participant * \
                           rec.provider_id.minimum_no_of_participants
                each_cost = min_cost / course_no_of_participants
            rec.unit_budget = each_cost

    def action_submit(self):
        """ Action Submit plan line """
        for line in self:
            if line.state == 'draft':
                user_id = line.tna_id.user_id.id or line.tna_id.create_uid
                # @formatter:off
                line._activity_schedule_with_view(
                    'mail.mail_activity_data_todo',
                    views_or_xmlid='hr_tna.hr_tna_line_search',
                    user_id=user_id,
                    summary='Set TNA provider for %s' %
                    line.department_id.name,
                )
                line.state = 'submitted'

    def action_budget(self):
        """ Action budget plan line """
        for line in self:
            if line.state == 'submitted':
                line.state = 'budgeted'
                for activity in line.activity_ids:
                    activity.action_done()

    def action_approve(self):
        """ Action Approve plan line """
        for line in self:
            if line.state == 'budgeted':
                if line.approved_no_of_participants == 0:
                    line.approved_no_of_participants = \
                        line.no_of_participants
                line.state = 'approved'
                dep_partner = line.department_id.manager_id.user_id.partner_id
                partners = dep_partner or line.tna_id.user_id.partner_id
                msg = _('%s plan was approved') % line.department_id.name
                line.message_post(
                    body=msg, message_type='notification',
                    partner_ids=partners.ids)

    def action_reject(self):
        """ Action Reject plan line """
        for line in self:
            if line.state == 'budgeted':
                line.state = 'rejected'
                dep_partner = line.department_id.manager_id.user_id.partner_id
                partners = dep_partner or line.tna_id.user_id.partner_id
                msg = _('%s plan was rejected') % line.department_id.name
                line.message_post(
                    body=msg, message_type='notification',
                    partner_ids=partners.ids
                )

    # pylint: disable=no-member
    def open_form(self):
        """open form"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'TNA Courses',
            'view_mode': 'form',
            'res_model': 'hr.tna.line',
            'res_id': self.id,
            'target': 'new',
            'context': {
                'form_view_initial_mode': 'edit',
            },
        }
