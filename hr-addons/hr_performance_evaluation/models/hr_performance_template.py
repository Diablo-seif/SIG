""" Initialize hr.performance.template """

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


# pylint: disable=no-member,protected-access
class HrPerformanceTemplate(models.Model):
    """
        init hr.performance.template:
    """
    _name = 'hr.performance.template'
    _description = 'HR Performance Template'
    _check_company_auto = True

    name = fields.Char(
        required=True,
    )
    active = fields.Boolean(
        default=True,
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        default=lambda self: self.env.company,
    )
    objective_line_ids = fields.One2many(
        comodel_name='hr.objective.template.line',
        inverse_name='template_id',
        copy=True,
    )
    objective_percentage = fields.Float(
        default=.7
    )
    job_id = fields.Many2one(
        comodel_name='hr.job',
        string='Job Position',
        required=True,
        check_company=True,
    )
    total_weightage = fields.Float(
        compute='_compute_total_weightage',
        store=True,
    )

    @api.depends('objective_line_ids', 'objective_line_ids.weightage')
    def _compute_total_weightage(self):
        """
        sum weightage
        """
        for rec in self:
            rec.total_weightage = sum(
                rec.objective_line_ids.mapped('weightage'))

    @api.constrains('objective_line_ids', 'total_weightage')
    def _check_total_weightage(self):
        """
        restrict total weightage more than 100
        """
        for rec in self:
            if rec.total_weightage != 1:
                raise ValidationError(_('Total weightage must be 100'))

    @api.constrains('job_id', 'active')
    def _check_job_duplicate(self):
        """
        restrict choose multi jobs
        """
        for rec in self:
            performances = self.search([('id', '!=', rec.id),
                                        ('job_id', '=', rec.job_id.id)])
            if performances:
                raise ValidationError(_('You can not link multi performance '
                                        'template with same job %s')
                                      % rec.job_id.display_name)

    @api.constrains('objective_line_ids', 'objective_percentage')
    def _check_performance_percentage(self):
        """
        restrict choose multi jobs
        """
        for rec in self:
            if rec.objective_percentage > 1:
                raise ValidationError(
                    _('Sum of objective percentage cannot exceed 100%')
                )
            if not rec.objective_line_ids and rec.objective_percentage:
                raise ValidationError(
                    _('Cannot add objective percentage '
                      'with empty objective lines')
                )
