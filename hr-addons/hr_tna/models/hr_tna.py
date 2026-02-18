""" HR Training Needs Assessment """
from dateutil.relativedelta import relativedelta

from odoo import SUPERUSER_ID, api, fields, models


# pylint: disable=no-member,protected-access
class HrTna(models.Model):
    """ HR Training Needs Assessment """
    _name = 'hr.tna'
    _description = 'Training Needs Assessment'
    _sql_constraints = [
        ('tna_date_check',
         'CHECK (date_from <= date_to)',
         'The start date must be anterior to the end date.'),
    ]
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(compute='_compute_name', store=True)
    state = fields.Selection([
        ('draft', 'Draft'), ('preparation', 'Preparation'),
        ('submitted', 'Submitted'), ('approved', 'Approved'), ('done', 'Done'),
        ('rejected', 'Rejected')], default='draft')
    department_ids = fields.Many2many(
        'hr.department', string='Shared to', required=True
    )
    tna_line_ids = fields.One2many(
        'hr.tna.line', 'tna_id', string='Department TNA Plan'
    )
    planned_budget = fields.Monetary(
        compute='_compute_budget', store=True, currency_field='currency_id',
    )
    approved_budget = fields.Monetary(
        compute='_compute_budget', store=True, currency_field='currency_id',
    )
    internal_budget = fields.Monetary(
        compute='_compute_budget', store=True, currency_field='currency_id',
    )
    external_budget = fields.Monetary(
        compute='_compute_budget', store=True, currency_field='currency_id',
    )
    currency_id = fields.Many2one(
        'res.currency', default=lambda self: self.env.company.currency_id.id
    )
    user_id = fields.Many2one(
        'res.users', string='Responsible', required=True,
        default=lambda self: self.env.uid,
        readonly=lambda self: not self.user.user_has_groups(
            'hr_tna.group_tna_manager'),
    )
    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)
    deadline = fields.Date(required=True)
    is_readonly = fields.Boolean(compute='_compute_is_readonly')

    def unlink(self):
        """
        Override unlink() to delete lines to unlink activity_ids
        because ondelete='cascade' unlink records in SQL
        """
        for rec in self:
            rec.tna_line_ids.unlink()
        return super().unlink()

    def _compute_is_readonly(self):
        """ Compute is_readonly value """
        for tna in self:
            tna.is_readonly = not self.user_has_groups(
                'hr_tna.group_tna_manager,hr.group_hr_manager'
            )

    @api.depends('tna_line_ids.planned_budget',
                 'tna_line_ids.approved_budget', 'tna_line_ids.state')
    def _compute_budget(self):
        """ Compute budget from tna lines budget """
        for tna in self:
            tna.approved_budget = sum(tna.tna_line_ids.filtered(
                lambda r: r.state == 'approved').mapped('approved_budget'))
            tna.planned_budget = sum(tna.mapped('tna_line_ids.planned_budget'))
            tna.internal_budget = sum(tna.tna_line_ids.filtered(
                lambda r: r.provider_type == 'internal'
            ).mapped('approved_budget'))
            tna.external_budget = sum(tna.tna_line_ids.filtered(
                lambda r: r.provider_type == 'external'
            ).mapped('approved_budget'))

    @api.depends('date_from', 'date_to')
    def _compute_name(self):
        """ Compute name value as TNA [start - end] """
        for tna in self:
            if tna.date_from:
                tna.name = 'TNA [%s - %s]' % (
                    tna.date_from or '', tna.date_to or '')

    def action_view_tna_lines(self):
        """
        View tna lines
        :return: tna lines action
        """
        tna_lines = self.mapped('tna_line_ids')
        action = self.env.ref(
            'hr_tna.hr_tna_line_action').sudo().read()[0]
        action['domain'] = [('id', 'in', tna_lines.ids)]
        return action

    def action_share(self):
        """
        Action Share Training Needs Assessment for departments managers
        """
        for tna in self:
            for department in tna.department_ids:
                user_id = department.manager_id.user_id.id or SUPERUSER_ID
                tna._activity_schedule_with_view(
                    'mail.mail_activity_data_todo',
                    views_or_xmlid='hr_tna.hr_tna_tree',
                    user_id=user_id,
                    summary="Set TNA for %s" % department.name,
                )
            tna.state = 'preparation'

    @api.model
    def action_deadline_submit(self):
        """ auto submit Training Needs Assessment on deadline """
        deadline = fields.Date.today() + relativedelta(days=+3)
        plans = self.search([('deadline', '<=', deadline)])
        for tna in plans:
            for department in tna.department_ids:
                user_id = department.manager_id.user_id.id or SUPERUSER_ID
                tna._activity_schedule_with_view(
                    'mail.mail_activity_data_todo',
                    views_or_xmlid='hr_tna.hr_tna_tree',
                    user_id=user_id,
                    summary="3 Days for Training Needs Assessment deadline"
                )
        plans = self.search([('deadline', '<', fields.Date.today())])
        plans.action_submit()

    def action_submit(self):
        """ Action Submit manpower tna """
        for tna in self:
            if tna.state == 'preparation':
                tna.state = 'submitted'

    def action_approve(self):
        """ Action Approve manpower tna """
        for tna in self:
            if tna.state == 'submitted':
                tna.tna_line_ids.action_approve()
                tna.state = 'approved'

    def action_reject(self):
        """ Action Reject manpower tna """
        for tna in self:
            if tna.state == 'submitted':
                tna.tna_line_ids.action_reject()
                tna.state = 'rejected'
