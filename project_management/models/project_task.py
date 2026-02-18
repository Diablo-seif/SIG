""" Initialize Project Task """

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProjectTask(models.Model):
    """
        Inherit Project Task:
         -
    """
    _inherit = 'project.task'

    weight = fields.Float(digits=(16, 15))
    remaining_planned_hours = fields.Float(
        # compute='_compute_remaining_planned_hours',
        store=True
    )

    # @api.depends('planned_hours', 'subtask_planned_hours')
    # def _compute_remaining_planned_hours(self):
    #     """ Compute remaining_planned_hours value """
    #     for rec in self:
    #         rec.remaining_planned_hours = rec.planned_hours - rec.subtask_planned_hours

    @api.constrains('weight')
    def _check_weight(self):
        """ Validate weight """
        for rec in self:
            tasks = rec.search([
                '|', ('project_id', '=', rec.project_id.id),
                ('parent_id.project_id', '=', rec.project_id.id)
            ])
            parent_weight = sum(tasks.filtered(
                lambda r: not r.parent_id and not r.child_ids).mapped(
                'weight'))
            child_weight = sum(tasks.filtered(lambda r: r.parent_id).mapped(
                lambda r: r.weight * r.parent_id.weight))
            total_weight = parent_weight + child_weight
            if total_weight > 1:
                raise ValidationError(
                    _('Total project tasks weight cannot exceed 100%'))
            if rec.weight < 0:
                raise ValidationError(_('Weight can only between 0% and  100%'))

    @api.constrains('planned_hours', 'subtask_planned_hours', 'parent_id')
    def _check_planned_hours(self):
        """ Validate planned_hours """
        for rec in self:
            if rec.subtask_planned_hours > rec.planned_hours:
                raise ValidationError(_(
                    f'Subtask planned hours cannot exceed parent planned hours [planned: {rec.planned_hours}, current: {rec.subtask_planned_hours}]'))
            if rec.parent_id:
                if rec.parent_id.subtask_planned_hours > rec.parent_id.planned_hours:
                    raise ValidationError(_(
                        f'Subtask planned hours cannot exceed parent planned hours [planned: {rec.parent_id.planned_hours}, current: {rec.parent_id.subtask_planned_hours}]'))
