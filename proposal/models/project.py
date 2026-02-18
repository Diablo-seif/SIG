""" Initialize Project """

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class ProjectProject(models.Model):
    """
        Inherit Project Project:
         -
    """
    _inherit = 'project.project'

    code = fields.Char()
    proposal_id = fields.Many2one(
        'proposal.proposal'
    )
    amendment_duration = fields.Integer()
    amendment_date = fields.Date(
        compute='_compute_amendment_date'
    )
    actual_start_date = fields.Date()
    actual_end_date = fields.Date()
    project_progress_status = fields.Selection(
        [('in_progress', 'In-Progress'),
         ('delayed', 'Delayed'),
         ('on_time', 'On-Time')],
        compute='_compute_project_progress_status'
    )

    @api.depends('actual_start_date', 'actual_end_date', 'date')
    def _compute_project_progress_status(self):
        """ Compute project_progress_status value """
        for rec in self:
            status = False
            if rec.actual_start_date:
                status = 'in_progress'
            if rec.actual_end_date:
                if rec.actual_end_date > rec.date:
                    status = 'delayed'
                else:
                    status = 'on_time'
            rec.project_progress_status = status

    @api.depends('amendment_duration', 'date')
    def _compute_amendment_date(self):
        """ Compute amendment_date value """
        for rec in self:
            amendment_date = rec.amendment_date
            if rec.date:
                amendment_date = rec.date + relativedelta(
                    days=rec.amendment_duration)
            rec.amendment_date = amendment_date

    def name_get(self):
        """
            Override name_get:
             - change display_name to be code - name
        """
        return self.mapped(lambda r: (r.id, f'[{r.code}] {r.name}'))

    def create_project_from_proposal(self):
        for rec in self:
            if rec.proposal_id:
                stages = self.env['project.task.type'].sudo().search([('user_id', '=', False)])
                for stage in stages:
                    stage.write({
                        'project_ids': [(4, rec.id)]
                    })
                stage_id = self.env['project.task.type'].sudo().search(
                    [('name', '=', 'New')], limit=1).id
                rec.task_ids = [(0, 0, {
                    'name': line.product_id.name,
                    # 'stage_id': rec.stage_find(rec.id, [('fold', '=', False)]),
                    'stage_id': stage_id,
                    'description': line.name,
                    'weight': line.price / rec.proposal_id.contracted_revenue or 0,
                    'planned_hours': line.product_uom_qty,
                }) for line in rec.proposal_id.line_ids.filtered(
                    lambda r: r.display_type == False)]
        return self.action_view_tasks()

    @api.model
    def create(self, vals_list):
        """ Override create """
        res = super().create(vals_list)
        sale = self.env.context.get('active_sale_id')
        if sale:
            so = self.env['sale.order'].browse(sale)
            so.project_created = True
            so.proposal_id.project_id = res.id
        return res
