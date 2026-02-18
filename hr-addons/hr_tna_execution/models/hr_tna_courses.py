""" HR TNA Courses """

from datetime import datetime, time, timedelta

import pytz

from odoo import _, fields, models

TIME_SELECTION = [
    ('0', '12:00 PM'), ('0.5', '0:30 AM'),
    ('1', '1:00 AM'), ('1.5', '1:30 AM'),
    ('2', '2:00 AM'), ('2.5', '2:30 AM'),
    ('3', '3:00 AM'), ('3.5', '3:30 AM'),
    ('4', '4:00 AM'), ('4.5', '4:30 AM'),
    ('5', '5:00 AM'), ('5.5', '5:30 AM'),
    ('6', '6:00 AM'), ('6.5', '6:30 AM'),
    ('7', '7:00 AM'), ('7.5', '7:30 AM'),
    ('8', '8:00 AM'), ('8.5', '8:30 AM'),
    ('9', '9:00 AM'), ('9.5', '9:30 AM'),
    ('10', '10:00 AM'), ('10.5', '10:30 AM'),
    ('11', '11:00 AM'), ('11.5', '11:30 AM'),
    ('12', '12:00 AM'), ('12.5', '0:30 PM'),
    ('13', '1:00 PM'), ('13.5', '1:30 PM'),
    ('14', '2:00 PM'), ('14.5', '2:30 PM'),
    ('15', '3:00 PM'), ('15.5', '3:30 PM'),
    ('16', '4:00 PM'), ('16.5', '4:30 PM'),
    ('17', '5:00 PM'), ('17.5', '5:30 PM'),
    ('18', '6:00 PM'), ('18.5', '6:30 PM'),
    ('19', '7:00 PM'), ('19.5', '7:30 PM'),
    ('20', '8:00 PM'), ('20.5', '8:30 PM'),
    ('21', '9:00 PM'), ('21.5', '9:30 PM'),
    ('22', '10:00 PM'), ('22.5', '10:30 PM'),
    ('23', '11:00 PM'), ('23.5', '11:30 PM')
]


# pylint: disable=too-many-arguments,protected-access,fixme
class HrTnaCourses(models.Model):
    """ inherit HR Tna Courses to start course """
    _inherit = 'hr.tna.courses'

    date_from = fields.Date()
    date_to = fields.Date()
    time_from = fields.Selection(TIME_SELECTION, string="Start Time")
    time_to = fields.Selection(TIME_SELECTION, string="End Time")

    def start_course(self, date_from, date_to, all_day,
                     time_from, time_to, leave_type):
        """ Start TNA Course """
        for course in self:
            if course.state == 'pending' and leave_type:
                calendar = course.employee_id.resource_calendar_id
                date_from = datetime.combine(
                    date_from, time(00, 00, 00)).replace(tzinfo=pytz.utc)
                date_to = datetime.combine(
                    date_to, time(23, 59, 59)).replace(tzinfo=pytz.utc)
                intervals = calendar._get_day_total(
                    date_from + timedelta(days=1),
                    date_to + timedelta(days=-1),
                    None
                )
                for day in intervals:
                    # FIXME something wrong with date_from and date_to
                    #  so i added a day to them to prevent constrains
                    vals = {
                        'holiday_type': 'employee',
                        'name': _('%s TNA Course') % course.course_id.name,
                        'employee_id': course.employee_id.id,
                        'holiday_status_id': leave_type.id,
                        'request_unit_hours': not all_day,
                        'request_date_from': day,
                        'request_date_to': day,
                        'request_hour_from': time_from,
                        'request_hour_to': time_to,
                    }
                    leave = self.env['hr.leave'].new(vals)
                    leave._compute_number_of_days()
                    leave._compute_number_of_days_display()
                    leave._compute_number_of_hours_display()
                    leave._compute_number_of_hours_text()
                    self.env['hr.leave'].create(
                        leave._convert_to_write(leave._cache))
                course.state = 'running'
                course.date_from = date_from
                course.date_to = date_to
                course.time_from = time_from
                course.time_to = time_to

    def end_course(self):
        """ End TNA Course """
        for course in self:
            if course.state == 'running':
                certification = course.tna_line_id.provider_id.certification_id
                course.employee_id.resume_line_ids = [(0, 0, {
                    'name': course.course_id.name,
                    'line_type_id': certification.id,
                    'date_start': course.date_from,
                    'date_end': course.date_to,
                    'description': course.course_id.description,
                })]
                course.state = 'done'
