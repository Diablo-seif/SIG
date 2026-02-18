""" HR Employee """
from odoo import api, fields, models


class HrEmployee(models.Model):
    """ inherit HR Employee """
    _inherit = 'hr.employee'

    planned_course_ids = fields.One2many(
        'hr.tna.courses', 'employee_id', groups="hr.group_hr_user"
    )
    course_count = fields.Integer(
        compute="_compute_course_count", string='Courses',
        groups="hr.group_hr_user"
    )

    @api.depends('planned_course_ids')
    def _compute_course_count(self):
        """ Compute course_count """
        for rec in self:
            rec.course_count = len(rec.planned_course_ids)

    def action_view_course(self):
        """ Smart button to run action """
        courses = self.mapped('planned_course_ids')
        action = self.env.ref(
            'hr_tna.hr_tna_courses_action').sudo().read()[0]
        action['domain'] = [('id', 'in', courses.ids)]
        return action
