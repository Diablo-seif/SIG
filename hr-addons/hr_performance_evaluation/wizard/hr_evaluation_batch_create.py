""" Initialize hr.evaluation.batch.create """

from odoo import _, fields, models
from odoo.exceptions import UserError


# pylint: disable=no-member
class HrEvaluationBatchCreate(models.TransientModel):
    """
    init hr.evaluation.batch.create
    """
    _name = 'hr.evaluation.batch.create'
    _description = 'HR Evaluation Batch Create Wizard'

    period_id = fields.Many2one(
        comodel_name='hr.evaluation.period',
        required=True,
        domain="['|', ('company_id', '=', False),"
               " ('company_id', '=', company_id)]",
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        default=lambda self: self.env.company,
    )
    start_date = fields.Date(
        related='period_id.start_date',
    )
    end_date = fields.Date(
        related='period_id.end_date',
    )
    deadline_date = fields.Date(
        string='Deadline',
    )
    employee_ids = fields.Many2many(
        comodel_name='hr.employee',
        domain="[('job_id', '!=', False), "
               "('job_id.performance_template_ids', '!=', False), "
               "('job_id.performance_template_ids.active', '=', True),"
               " '|', ('company_id', '=', False),"
               " ('company_id', '=', company_id)]"
    )

    def action_create_evaluation(self):
        """
        create multi evaluation
        """
        if not self.employee_ids:
            raise UserError(_('Please choose employee!'))
        evaluations = self.env['hr.evaluation']
        for employee in self.employee_ids:
            evaluation = evaluations.create({
                'employee_id': employee.id,
                'period_id': self.period_id.id,
                'start_date': self.period_id.start_date,
                'end_date': self.period_id.end_date,
                'deadline_date': self.deadline_date,
                'performance_template_id': employee.job_id.performance_template_ids.id,
                'company_id': self.company_id.id,
            })
            evaluation._onchange_performance_template()
            evaluations += evaluation
        if evaluations:
            return {
                'name': _('Evaluations'),
                'view_mode': 'list,form',
                'res_model': 'hr.evaluation',
                'type': 'ir.actions.act_window',
                'target': 'current',
                'domain': [('id', 'in', evaluations.ids)],
                'context': {'create': False},
            }
