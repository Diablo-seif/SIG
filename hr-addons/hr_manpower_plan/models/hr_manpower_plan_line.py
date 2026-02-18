""" Manpower plan """

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


# pylint: disable=protected-access,no-member,duplicate-code
class HrManpowerPlanLine(models.Model):
    """ HR Manpower Plan Line """
    _name = 'hr.manpower.plan.line'
    _description = 'Department Manpower Plan'
    _rec_name = 'department_id'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _sql_constraints = [
        ('unique_job',
         'UNIQUE(department_id,job_id,manpower_plan_id,reason,start_date)',
         _("Plan line can't be duplicated")),
    ]

    @api.model
    def _get_department_domain(self):
        if self.user_has_groups(
                'hr_manpower_plan.group_manpower_plan_manager'):
            return []
        return [('manager_id', '=', self.env.user.employee_id.id)]

    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('budgeted', 'Budgeted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], default='draft', readonly=True, tracking=True)
    department_id = fields.Many2one(
        'hr.department', domain=lambda self: self._get_department_domain(),
        default=lambda self: self.env['hr.department'].search(
            [('manager_id', '=', self.env.user.employee_id.id)], limit=1).id,
        required=True
    )
    job_id = fields.Many2one('hr.job', string='Position', required=True)
    no_of_employee = fields.Integer(
        compute='_compute_no_of_employee', store=True,
        string='Current No. Of Employees'
    )
    planned_no_of_position = fields.Integer(tracking=True)
    approved_no_of_position = fields.Integer(tracking=True)
    reason = fields.Selection([
        ('new_hire', 'New Hire'),
        ('replacement', 'Replacement')
    ], required=True, default='new_hire')
    start_date = fields.Date(string='Estimated Starting Date')
    current_budget = fields.Monetary(
        compute='_compute_current_budget', store=True,
    )
    unit_budget = fields.Monetary()
    total_budget = fields.Monetary(
        compute='_compute_total_budget', store=True,
    )
    approved_budget = fields.Monetary(
        compute='_compute_total_budget', store=True,
    )
    actual_budget = fields.Monetary(
        compute='_compute_actual_budget', store=True,
    )
    note = fields.Text(tracking=True, readonly=True)
    currency_id = fields.Many2one(
        'res.currency', default=lambda self: self.env.company.currency_id.id
    )
    manpower_plan_id = fields.Many2one('hr.manpower.plan', ondelete='cascade')

    @api.constrains('planned_no_of_position', 'reason')
    def _check_planned_no_of_position(self):
        """ Validate planned_no_of_position """
        for rec in self:
            if rec.planned_no_of_position > rec.no_of_employee and \
                    rec.reason == "replacement":
                raise ValidationError(_(
                    'In case of replacement the planned number of positions '
                    'can\'t be more than current number of positions'
                ))

    @api.constrains('start_date')
    def _check_start_date(self):
        """ Validate start_date not to exceed overall manpower end date """
        for plan_line in self:
            plan_from = plan_line.manpower_plan_id.date_from
            plan_to = plan_line.manpower_plan_id.date_to
            if plan_line.start_date < plan_from or \
                    plan_line.start_date > plan_to:
                raise ValidationError(
                    _('Estimated Starting Date '
                      'must be between %(plan_from)s and %(plan_to)s') % {
                          "plan_from": plan_from,
                          "plan_to": plan_to
                      }
                )

    @api.depends(
        'planned_no_of_position', 'approved_no_of_position', 'unit_budget'
    )
    def _compute_total_budget(self):
        """ Compute Total budget value """
        for plan_line in self:
            if plan_line.reason == 'replacement':
                current_salary = 0
                if plan_line.job_id.salary_type == 'fixed':
                    current_salary = plan_line.job_id.salary
                elif plan_line.job_id.salary_type == 'range':
                    current_salary = plan_line.job_id.max_salary
                diff = max(plan_line.unit_budget - current_salary, 0)
                plan_line.total_budget = plan_line.planned_no_of_position * diff
                plan_line.approved_budget = \
                    plan_line.approved_no_of_position * diff
            else:
                plan_line.total_budget = \
                    plan_line.planned_no_of_position * plan_line.unit_budget
                plan_line.approved_budget = \
                    plan_line.approved_no_of_position * plan_line.unit_budget

    @api.depends('job_id')
    def _compute_current_budget(self):
        """ compute current employees budget """
        for rec in self:
            contracts = rec.job_id.employee_ids.mapped(
                'contract_id').filtered(lambda r: r.state == 'open')
            rec.current_budget = sum(contracts.mapped('wage'))

    @api.depends('current_budget', 'approved_budget')
    def _compute_actual_budget(self):
        for rec in self:
            rec.actual_budget = rec.approved_budget + rec.current_budget

    @api.depends('job_id')
    def _compute_no_of_employee(self):
        """ job_id """
        for rec in self:
            rec.no_of_employee = rec.job_id.no_of_employee

    def action_submit(self):
        """ Action Submit plan line """
        for plan_line in self:
            if plan_line.state == 'draft':
                user_id = plan_line.manpower_plan_id.user_id.id or \
                          plan_line.manpower_plan_id.create_uid
                dep_name = plan_line.department_id.name
                if plan_line.job_id.salary_type == 'fixed':
                    plan_line.sudo().unit_budget = plan_line.job_id.salary
                elif plan_line.job_id.salary_type == 'range':
                    plan_line.sudo().unit_budget = plan_line.job_id.max_salary
                plan_line._activity_schedule_with_view(
                    'mail.mail_activity_data_todo',
                    views_or_xmlid='hr_manpower_plan.'
                                   'hr_manpower_plan_line_tree',
                    user_id=user_id,
                    summary='Set manpower budget for %s' % dep_name,
                )
                plan_line.state = 'submitted'

    def action_budget(self):
        """ Action budget plan line """
        for plan_line in self:
            if plan_line.state == 'submitted':
                plan_line.state = 'budgeted'
                for activity in plan_line.activity_ids:
                    activity.action_done()

    def action_approve(self):
        """ Action Approve plan line """
        for plan_line in self:
            if plan_line.state == 'budgeted':
                if plan_line.approved_no_of_position == 0:
                    plan_line.approved_no_of_position = \
                        plan_line.planned_no_of_position
                plan_line.state = 'approved'
                dep_partner = plan_line.department_id. \
                    manager_id.user_id.partner_id
                # @formatter:off
                partners = dep_partner or \
                    plan_line.manpower_plan_id.user_id.partner_id
                msg = _('%s plan was Approved') % plan_line.department_id.name
                plan_line.message_post(
                    body=msg, message_type='notification',
                    partner_ids=partners.ids)

    def action_reject(self):
        """ Action Reject plan line """
        for plan_line in self:
            if plan_line.state == 'budgeted':
                plan_line.approved_no_of_position = 0
                plan_line.state = 'rejected'
                dep_partner = plan_line.department_id. \
                    manager_id.user_id.partner_id
                partners = dep_partner or \
                    plan_line.manpower_plan_id.user_id.partner_id
                msg = _('%s plan was rejected') % plan_line.department_id.name
                plan_line.message_post(
                    body=msg, message_type='notification',
                    partner_ids=partners.ids)
