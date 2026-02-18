""" update object employee"""

from datetime import datetime

from odoo import api, fields, models


class HrEmployee(models.Model):
    """ update object employee"""
    _inherit = 'hr.employee'

    # pylint: disable=no-member
    @api.model
    def get_deduction_penalties(self, date_form=None, date_to=None,
                                deduction_type='percentage'):
        """
        Function to get deduction penalties.
        :return: Float Value
        """
        value = 0
        if date_form and date_to and self.id:
            attendance_records = self.env['hr.attendance.record'].search(
                [('employee_id', '=', self.id),
                 ('date', '>=', date_form),
                 ('date', '<=', date_to), ]
            )
            if deduction_type == 'percentage':
                value = \
                    sum(attendance_records.mapped('total_penalty_percentage'))
            if deduction_type == 'amount':
                value = \
                    sum(attendance_records.mapped('total_penalty_amount'))
        return value * -1

    # pylint: disable=no-member, cell-var-from-loop
    @api.model
    def get_week_deduction_hours(self, date_form=None, date_to=None):
        """
        Function to get week deduction hours.
        :return: Float Value (week_deduction_hours)
        """
        self.ensure_one()
        value = 0
        if not date_form or not date_to or not self.id:
            return False
        if not isinstance(date_form, datetime):
            date_form = fields.Datetime.to_string(date_form)
        if not isinstance(date_to, datetime):
            date_to = fields.Datetime.to_string(date_to)
        attendance_records = self.env['hr.attendance.record'].search(
            [('employee_id', '=', self.id),
             ('date', '>=', date_form),
             ('date', '<=', date_to),
             ('attend_interval', '>', 0), ]
        ).filtered(lambda rec: not rec.absent_interval)
        list_weeks = []
        for record in attendance_records:
            if record.weekday not in list_weeks:
                list_weeks.append(record.weekday)
        for one_week in list_weeks:
            total_actual_working_hours = 0
            must_week_hours = 0
            week_attendance_records = attendance_records.filtered(
                lambda rec: rec.weekday == one_week)
            for rec_id in week_attendance_records:
                total_actual_working_hours += rec_id.total_actual_working_hours
                must_week_hours += rec_id.working_schedule_hours
            if must_week_hours > total_actual_working_hours:
                value += must_week_hours - total_actual_working_hours
        return value * -1

    # pylint: disable=no-member
    @api.model
    def get_month_deduction_hours(self, date_form=None, date_to=None):
        """
        Function to get month deduction hours.
        :return: Float Value (week_deduction_hours)
        """
        self.ensure_one()
        value = 0
        if not date_form or not date_to or not self.id:
            return False
        if not isinstance(date_form, datetime):
            date_form = fields.Datetime.to_string(date_form)
        if not isinstance(date_to, datetime):
            date_to = fields.Datetime.to_string(date_to)
        attendance_records = self.env['hr.attendance.record'].search(
            [('employee_id', '=', self.id),
             ('date', '>=', date_form),
             ('date', '<=', date_to),
             ('attend_interval', '>', 0), ]
        )
        total_actual_working_hours = 0
        must_month_hours = 0
        for rec_id in attendance_records:
            total_actual_working_hours += rec_id.total_actual_working_hours
            must_month_hours += rec_id.working_schedule_hours
        if must_month_hours > total_actual_working_hours:
            value += must_month_hours - total_actual_working_hours
        return value * -1
