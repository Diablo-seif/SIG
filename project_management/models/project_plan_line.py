
from odoo import fields, models, api, _
from odoo.exceptions import UserError


class ProjectPlanLine(models.Model):

    _name = 'project.plan.line'
    _description = 'Project Plan Line'

    project_id = fields.Many2one('project.project')
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    target = fields.Float(required=True)
    # cumulative_target = fields.Float(compute="_compute_cumulative_target")
    cumulative_target = fields.Float(readonly=True)
    # actual_progress = fields.Float(compute="_compute_actual_progress")
    actual_progress = fields.Float(readonly=True)
    

    @api.constrains('start_date')
    def _constrains_start_date(self):
        for rec in self:
            if rec.start_date < rec.project_id.date_start:
                raise UserError(_("'Start Date' must be after Project Start Date."))
            
    # @api.depends('target')
    # def _compute_cumulative_target(self):
    #     for record in self:
    #         if record.end_date:
    #             record.cumulative_target = sum(record.project_id.project_plan_line_ids.filtered(
    #                     lambda r: r.end_date <= record.end_date and r.id).mapped('target'))
    #         else:
    #             record.cumulative_target = 0
  
  
    # def _compute_actual_progress(self):
    #     for record in self:
    #         record.actual_progress = 0
    #         for task in record.project_id.task_ids:
    #             if task.planned_hours > 0:
    #                 task_progress =  (sum(task.timesheet_ids.filtered(
    #                     lambda r: r.date <= record.end_date).mapped('unit_amount'))
    #                                 / task.planned_hours) * task.weight
    #                 record.actual_progress += task_progress
            