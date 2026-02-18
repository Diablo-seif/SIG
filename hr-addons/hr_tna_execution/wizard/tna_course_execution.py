""" Tna Start Course """
# pylint: disable=protected-access,import-error,odoo-addons-relative-import
from odoo.addons.hr_tna_execution.models.hr_tna_courses import TIME_SELECTION

from odoo import _, api, fields, models


class TnaCourseExecution(models.TransientModel):
    """ Tna Start Course """
    _name = 'tna.course.execution'
    _description = 'Course Execution'

    leave_type_id = fields.Many2one('hr.leave.type', 'Time Off Type')
    execution_line_ids = fields.One2many(
        'course.execution.line', 'execution_id'
    )

    def start_course(self):
        """ Start TNA Course """
        for rec in self:
            rec.execution_line_ids.start_course()

    def end_course(self):
        """ Rnd TNA Course """
        for rec in self:
            rec.execution_line_ids.end_course()


class CourseExecutionLine(models.TransientModel):
    """ Execution Line """
    _name = 'course.execution.line'
    _description = 'Course Execution Line'
    _sql_constraints = [
        ('check_date_from_before_date_to',
         'CHECK(1 = 1)',
         _('Start date must be anterior to the end date')),
        ('check_time_from_before_time_to',
         'CHECK(1 = 1)',
         _('Start time must be anterior to the end time.')),
    ]

    @api.model
    def _get_tna_courses(self):
        """ Get TNA Courses to be used when start course """
        tnas = self.env['hr.tna'].browse(self.env.context.get('active_ids'))
        state = 'pending' if \
            self.env.context.get('action') == 'start' else 'running'
        courses = tnas.tna_line_ids.tna_course_ids.filtered(
            lambda r: r.state == state)
        return courses

    @api.model
    def _domain_course(self):
        """ Add domain to filter course based on pending TNA courses """
        courses = self._get_tna_courses()
        return [('id', 'in', courses.mapped('course_id').ids)]

    tna_courses_ids = fields.Many2many(
        'hr.tna.courses', default=lambda self: self._get_tna_courses().ids
    )
    course_id = fields.Many2one(
        'hr.course', domain=_domain_course, required=True)
    employee_ids = fields.Many2many('hr.employee', required=True)
    date_from = fields.Date()
    date_to = fields.Date()
    all_day = fields.Boolean()
    time_from = fields.Selection(TIME_SELECTION, string="Start Time")
    time_to = fields.Selection(TIME_SELECTION, string="End Time")
    execution_id = fields.Many2one('tna.course.execution')

    @api.onchange('course_id')
    def _onchange_course_id(self):
        """ filter employees based on employees that joining TNA course """
        employees = self._get_tna_courses().filtered(
            lambda r: r.course_id == self.course_id).mapped('employee_id')
        self.employee_ids = employees.ids
        return {'domain': {
            'employee_ids': [('id', 'in', employees.ids)]
        }}

    @api.onchange('course_id', 'employee_ids')
    def _onchange_filter_tna_courses(self):
        """ filter TNA courses that will be started """
        self.tna_courses_ids = self._get_tna_courses().filtered(
            lambda r: r.course_id == self.course_id and
            r.employee_id.id in self.employee_ids.ids).ids or [(5,)]

    def start_course(self):
        """ Start Course """
        for rec in self:
            rec.tna_courses_ids.start_course(
                date_from=rec.date_from,
                date_to=rec.date_to,
                all_day=rec.all_day,
                time_from=rec.time_from,
                time_to=rec.time_to,
                leave_type=rec.execution_id.leave_type_id,
            )

    def end_course(self):
        """ Start Course """
        for rec in self:
            rec.tna_courses_ids.end_course()
