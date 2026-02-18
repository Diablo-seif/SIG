""" init hr.evaluation.performance.line """
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HrEvaluationPerformanceLine(models.Model):
    """
    init hr.evaluation.performance.line
    """
    _name = 'hr.evaluation.performance.line'
    _description = 'HR Evaluation Performance Lines'

    evaluation_id = fields.Many2one(
        comodel_name='hr.evaluation',
        ondelete='cascade',
    )
    name = fields.Char(
        string='Key Performance Area',
        required=True,
    )
    description = fields.Text()
    hint = fields.Char()
    weightage = fields.Float(
        default=.1,
    )
    sequence = fields.Integer(
        default=10,
    )
    display_type = fields.Selection(
        selection=[
            ('line_section', "Section")],
        default=False,
        help="Technical field for UX purpose.",
    )
    final_rating = fields.Float()
    final_remark = fields.Text()
    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        related='evaluation_id.employee_id',
        store=True,
    )
    performance_template_id = fields.Many2one(
        comodel_name='hr.performance.template',
        related='evaluation_id.performance_template_id',
        store=True,
    )
    period_id = fields.Many2one(
        comodel_name='hr.evaluation.period',
        related='evaluation_id.period_id',
        store=True,
    )
    start_date = fields.Date(
        related='evaluation_id.start_date',
        store=True,
    )
    end_date = fields.Date(
        related='evaluation_id.end_date',
        store=True,
    )
    final_score_percentage = fields.Float(
        compute='_compute_final_score_percentage',
        store=True,
    )

    @api.constrains('final_rating')
    def _check_negative_rating(self):
        """
        restrict add negative rating
        """
        for record in self:
            if record.final_rating < 0:
                raise ValidationError(_('Rating must be positive!'))

    @api.depends('final_rating', 'weightage')
    def _compute_final_score_percentage(self):
        """
        compute score based on weight and rating
        """
        for record in self:
            record.final_score_percentage = (
                        record.weightage * record.final_rating)
