""" Manpower Plan Recruitment """
from odoo import fields, models


class ManpowerRecruitment(models.TransientModel):
    """ Manpower Recruitment """
    _name = 'manpower.recruitment'
    _description = 'Manpower Recruitment'

    plan_id = fields.Many2one('hr.manpower.plan')
    recruitment_method = fields.Selection([
        ('replace', 'Replace (no.of vacancies = planned no.of vacancies)'),
        ('add', 'Add to (no.of vacancies + planned no.of vacancies)')
    ], required=True)

    def action_start_recruitment(self):
        """ Start Recruitment process """
        self.plan_id.start_recruitment(method=self.recruitment_method)
