""" Manpower plan """

from dateutil.relativedelta import relativedelta

from odoo import SUPERUSER_ID, _, api, fields, models
from odoo.exceptions import UserError


# pylint: disable=no-member,protected-access
class HrManpowerPlan(models.Model):
    """ Manpower Plan """
    _name = 'hr.manpower.plan'
    _description = 'Manpower Plan'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _sql_constraints = [(
        'date_check',
        'CHECK ((date_from <= date_to))',
        _('The start date must be anterior to the end date.')
    )]

    name = fields.Char(compute='_compute_name', store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('preparation', 'Preparation'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('done', 'Done'),
        ('rejected', 'Rejected')], default='draft')
    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)
    deadline = fields.Date(required=True)
    department_ids = fields.Many2many(
        'hr.department', string='Shared to', required=True
    )
    manpower_line_ids = fields.One2many(
        'hr.manpower.plan.line', 'manpower_plan_id'
    )
    planned_budget = fields.Monetary(
        compute='_compute_budget', store=True, currency_field='currency_id',
    )
    approved_budget = fields.Monetary(
        compute='_compute_budget', store=True, currency_field='currency_id',
    )
    current_budget = fields.Monetary(
        compute='_compute_budget', store=True, currency_field='currency_id',
    )
    actual_budget = fields.Monetary(
        compute='_compute_budget', store=True, currency_field='currency_id',
    )
    currency_id = fields.Many2one(
        'res.currency', default=lambda self: self.env.company.currency_id.id
    )
    user_id = fields.Many2one(
        'res.users', string='Responsible', required=True,
        default=lambda self: self.env.uid,
        readonly=lambda self: not self.user.user_has_groups(
            'hr_manpower_plan.group_manpower_plan_manager'),
    )
    is_readonly = fields.Boolean(compute='_compute_is_readonly')

    def unlink(self):
        """
        Override unlink() to delete lines to unlink activity_ids
        because ondelete='cascade' unlink records in SQL
        """
        for rec in self:
            rec.manpower_line_ids.unlink()
        return super().unlink()

    def _compute_is_readonly(self):
        """ Compute is_readonly value """
        for plan in self:
            plan.is_readonly = not self.user_has_groups(
                'hr_manpower_plan.group_manpower_plan_manager,'
                'hr.group_hr_manager'
            )

    @api.depends('manpower_line_ids.total_budget', 'manpower_line_ids.state')
    def _compute_budget(self):
        """ Compute budget from plan lines budget """
        for plan in self:
            plan.planned_budget = sum(
                plan.mapped('manpower_line_ids.total_budget')
            )
            plan.current_budget = sum(
                plan.mapped('manpower_line_ids.current_budget')
            )
            plan.actual_budget = sum(
                plan.mapped('manpower_line_ids.actual_budget')
            )
            plan.approved_budget = sum(
                plan.manpower_line_ids.filtered(
                    lambda r: r.state == 'approved'
                ).mapped('approved_budget')
            )

    @api.depends('date_from', 'date_to')
    def _compute_name(self):
        """ Compute name value as PLAN [start - end] year """
        for plan in self:
            if plan.date_from:
                plan.name = 'PLAN [%s - %s]' % (
                    plan.date_from or '', plan.date_to or '')

    def action_view_plan_lines(self):
        """
        View plan lines
        :return: plan lines action
        """
        plan_lines = self.mapped('manpower_line_ids')
        action = self.env.ref(
            'hr_manpower_plan.hr_manpower_plan_line_action').sudo().read()[0]
        action['domain'] = [('id', 'in', plan_lines.ids)]
        return action

    def action_share(self):
        """ Action Share Manpower Plan for departments managers """
        for plan in self:
            for department in plan.department_ids:
                user_id = department.manager_id.user_id.id or SUPERUSER_ID
                plan._activity_schedule_with_view(
                    'mail.mail_activity_data_todo',
                    views_or_xmlid='hr_manpower_plan.hr_manpower_plan_tree',
                    user_id=user_id,
                    summary="Set manpower for %s" % department.name,
                )
            plan.state = 'preparation'

    @api.model
    def action_deadline_submit(self):
        """ auto submit manpower plan on deadline """
        deadline = fields.Date.today() + relativedelta(days=+3)
        plans = self.search([('deadline', '<=', deadline)])
        for plan in plans:
            for department in plan.department_ids:
                user_id = department.manager_id.user_id.id or SUPERUSER_ID
                plan._activity_schedule_with_view(
                    'mail.mail_activity_data_todo',
                    views_or_xmlid='hr_manpower_plan.hr_manpower_plan_tree',
                    user_id=user_id,
                    summary="3 Days for Manpower plan deadline"
                )
        plans = self.search([('deadline', '<', fields.Date.today()),
                             ('state', '=', 'preparation')])
        for plan in plans:
            plan.action_submit()

    def action_submit(self):
        """ Action Submit manpower plan """
        for plan in self:
            if plan.state == 'preparation':
                plan.state = 'submitted'

    def action_approve(self):
        """ Action Approve manpower plan """
        for plan in self:
            if plan.state == 'submitted':
                for line in plan.manpower_line_ids:
                    line.action_approve()
                plan.state = 'approved'

    def action_reject(self):
        """ Action Reject manpower plan """
        for plan in self:
            if plan.state == 'submitted':
                for line in plan.manpower_line_ids:
                    line.action_reject()
                plan.state = 'rejected'

    def action_start_recruitment(self):
        """
        return wizard to choose recruitment method and start recruitment
        """
        self.ensure_one()
        action = self.env.ref(
            'hr_manpower_plan.manpower_recruitment_action'
        ).sudo().read()[0]
        action['context'] = {
            'default_plan_id': self.id,
        }
        return action

    def start_recruitment(self, method):
        """
        Start Recruitment open vacancies with the approved plan lines
        """
        for plan in self:
            lines = plan.manpower_line_ids
            lines = lines.filtered(lambda r: r.state == 'approved')
            for line in lines:
                if method == 'replace':
                    line.job_id.no_of_recruitment = line.approved_no_of_position
                    plan.state = 'done'
                elif method == 'add':
                    line.job_id.no_of_recruitment = \
                        line.job_id.no_of_recruitment + \
                        line.approved_no_of_position
                    plan.state = 'done'
                else:
                    raise UserError(_('Please use recruitment method'))
