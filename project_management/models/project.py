""" Initialize Project """

from odoo import api, fields, models


class ProjectProject(models.Model):
    """
        Inherit Project Project:
         -
    """
    _inherit = 'project.project'

    progress = fields.Float(
        compute='_compute_progress',
        store=True
    )
    allocated_hours = fields.Float(
        compute='_compute_allocated_hours',
        store=True
    )
    date_start = fields.Date(required=True)
    project_plan_line_ids = fields.One2many('project.plan.line', 'project_id')
    total_target_percentage = fields.Float(compute="_compute_total_target_percentage")
    contract_received_planned_date = fields.Date()
    contract_received_actual_date = fields.Date()
    site_handover_planned_date = fields.Date()
    site_handover_actual_date = fields.Date()
    down_payment_received_planned_date = fields.Date()
    down_payment_received_actual_date = fields.Date()
    amendment_date = fields.Date(tracking=True)
    tag_id = fields.Many2one('project.tags')

    @api.depends('project_plan_line_ids')
    def _compute_total_target_percentage(self):
        """ Compute total_target_percentage value """
        for rec in self:
            rec.total_target_percentage = sum(rec.project_plan_line_ids.mapped('target'))
            
            """ Compute project_plan_line cumulative_target value """
            for record in rec.project_plan_line_ids:
                if record.end_date:
                    record.cumulative_target = sum(rec.project_plan_line_ids.filtered(
                            lambda r: r.end_date <= record.end_date).mapped('target'))

                
                """ Compute project_plan_line actual_progress value """
                record.actual_progress = 0
                for task in rec.task_ids:
                    if task.planned_hours > 0:
                        task_progress =  (sum(task.timesheet_ids.filtered(
                            lambda r: r.date <= record.end_date).mapped('unit_amount'))
                                        / task.planned_hours) * task.weight
                        record.actual_progress += task_progress
            
            
    #
    # @api.depends('task_ids', 'task_ids.planned_hours')
    @api.depends('task_ids')
    def _compute_allocated_hours(self):
        """ Compute allocated_hours value """
        for rec in self:
            rec.allocated_hours = sum(rec.task_ids.mapped('planned_hours'))

    @api.depends('task_ids.weight', 'task_ids.progress')
    def _compute_progress(self):
        """ Compute progress value """
        for rec in self:
            parent_progress = sum(
                rec.task_ids.filtered(
                    lambda r: not r.parent_id and not r.child_ids).mapped(
                    lambda r: r.weight * (r.progress / 100)))
            child_progress = sum(
                rec.task_ids.filtered(lambda r: r.parent_id).mapped(
                    lambda r: r.parent_id.weight * r.weight * (
                            r.progress / 100)))
            rec.progress = parent_progress + child_progress
