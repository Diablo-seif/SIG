""" init object hr_compute_attendance"""

import logging
from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import fields, models
from .hr_compute_attendance import MONTH_SELECTION

LOGGER = logging.getLogger(__name__)


# pylint: disable=no-member
class HrComputeAttendanceLine(models.Model):
    """ init object hr_compute_attendance.line"""
    _name = 'hr.compute.attendance.line'
    _description = 'Compute Attendance Lines'

    def name_get(self):
        """
        Override name Get.
        """
        res = []
        for line in self:

            month_str = dict(MONTH_SELECTION).get(line.compute_id.month, "")
            employee_name = ""
            if line.employee_id:
                employee_name = line.employee_id.name
            name = "Compute Attendance For %s In Month %s" % (employee_name,
                                                              month_str)
            res.append((line.id, name))
        return res

    def open_line(self):
        """
        View List of attendance records related to this line of data.
        :return:
        """
        self.ensure_one()
        # pylint: disable=protected-access
        action = self.env["ir.actions.actions"]._for_xml_id(
            "hr_compute_attendance.view_hr_attendance_record_action")
        action['context'] = {'search_default_employee_id': self.employee_id.id}
        action['domain'] = [('date', '>=', self.start_date),
                            ('date', '<=', self.end_date)]
        return action

    # pylint: disable=too-many-locals, too-many-statements,too-many-branches

    def compute_line(self):
        """
        Compute Attendance for employee in month duration.
        """
        compute_obj = self.env['hr.compute.attendance']
        dict_month = dict(compute_obj.fields_get(
            allfields=['month'])['month']['selection'])
        for rec in self:
            interval_ids = self.env['hr.attendance.interval']
            record_ids = self.env['hr.attendance.record']
            sum_working_schedule_hours = 0
            sum_total_actual_working_hours = 0
            sum_total_missing_hours = 0
            sum_total_penalty_percentage = 0
            sum_total_penalty_amount = 0
            sum_attend_interval = 0
            sum_interval_count = 0
            sum_absent_interval = 0
            sum_absent_penalty_value = 0
            if rec.employee_id and rec.start_date and rec.end_date:
                start_date = rec.start_date
                end_date = rec.end_date
                this_day = start_date
                month = dict_month[rec.compute_id.month]
                while this_day <= end_date:
                    weekday = this_day.strftime("%U")
                    LOGGER.info("Compute Line Attendance: %s | %s.",
                                rec.employee_id.name, this_day)
                    record_id = self.env['hr.attendance.record'].search(
                        [('date', '=', this_day),
                         ('employee_id', '=', rec.employee_id.id)], limit=1)
                    if not record_id:
                        record_id = self.env['hr.attendance.record'].create({
                            'employee_id': rec.employee_id.id,
                            'date': this_day,
                            'weekday': weekday,
                            'month': month,
                        })
                    else:
                        values = {'interval_ids': [(5,)]}
                        if record_id.weekday != weekday:
                            values['weekday'] = weekday
                        if record_id.month != month:
                            values['month'] = month
                        if values:
                            record_id.write(values)
                    record_id.update_record()
                    record_ids |= record_id
                    if record_id.interval_ids:
                        interval_ids |= record_id.interval_ids
                    this_day = this_day + relativedelta(days=1)
                # --------------- end while loop ---------------
                # calculate penalty in redundancy
                penalty_in_ids = interval_ids.mapped("penalty_in_id")
                # pylint: disable=cell-var-from-loop
                for penalty_in in penalty_in_ids:
                    interval_penalty_in = interval_ids.filtered(
                        lambda interval: interval.penalty_in_id == penalty_in)
                    i = 1
                    for interval_id in interval_penalty_in:
                        interval_id.penalty_in_redundant = i
                        i += 1
                # calculate penalty out redundancy
                penalty_out_ids = interval_ids.mapped("penalty_out_id")
                for penalty_out in penalty_out_ids:
                    interval_penalty_out = interval_ids.filtered(
                        lambda interval: interval.penalty_out_id == penalty_out)
                    i = 1
                    for interval_id in interval_penalty_out:
                        interval_id.penalty_out_redundant = i
                        i += 1
                # calculate absent redundancy
                absent_intervals = interval_ids.filtered(
                    lambda interval: not interval.is_attend)
                i = 1
                for interval_id in absent_intervals:
                    interval_id.absent_redundant = i
                    i += 1
                # calculate penalty missing hours redundancy
                penalty_missing_ids = interval_ids.mapped("penalty_missing_id")
                for penalty_missing in penalty_missing_ids:
                    interval_penalty_missing = interval_ids.filtered(
                        lambda intv: intv.penalty_missing_id == penalty_missing)
                    i = 1
                    for interval_id in interval_penalty_missing:
                        interval_id.penalty_missing_redundant = i
                        i += 1
                rec.last_computed = datetime.now()
            for record_id in record_ids:
                sum_working_schedule_hours += record_id. \
                    working_schedule_hours
                sum_total_actual_working_hours += record_id. \
                    total_actual_working_hours
                sum_total_missing_hours += record_id.total_missing_hours
                sum_total_penalty_percentage += \
                    record_id.total_penalty_percentage
                sum_total_penalty_amount += record_id.total_penalty_amount
                sum_attend_interval += record_id.attend_interval
                sum_interval_count += record_id.interval_count
                sum_absent_interval += record_id.absent_interval
                sum_absent_penalty_value += record_id.absent_penalty_value
            rec.sum_working_schedule_hours = sum_working_schedule_hours
            rec.sum_total_actual_working_hours = sum_total_actual_working_hours
            rec.sum_total_missing_hours = sum_total_missing_hours
            rec.sum_total_penalty_percentage = sum_total_penalty_percentage
            rec.sum_total_penalty_amount = sum_total_penalty_amount
            rec.sum_attend_interval = sum_attend_interval
            rec.sum_interval_count = sum_interval_count
            rec.sum_absent_interval = sum_absent_interval
            rec.sum_absent_penalty_value = sum_absent_penalty_value

    def _compute_week_deduction_hours(self):
        """"
        Compute week_deduction_hours
        """
        for rec in self:
            rec.week_deduction_hours = abs(
                rec.employee_id.get_week_deduction_hours(
                    rec.start_date, rec.end_date)
            )

    def _compute_month_deduction_hours(self):
        """"
        Compute month_deduction_hours
        """
        for rec in self:
            rec.month_deduction_hours = abs(
                rec.employee_id.get_month_deduction_hours(
                    rec.start_date, rec.end_date)
            )

    compute_id = fields.Many2one(comodel_name="hr.compute.attendance")
    employee_id = fields.Many2one(comodel_name="hr.employee", required=True)
    department_id = fields.Many2one(comodel_name="hr.department",
                                    related="employee_id.department_id",
                                    store=True)
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    last_computed = fields.Datetime()
    sum_working_schedule_hours = fields.Float()
    sum_total_actual_working_hours = fields.Float()
    sum_total_missing_hours = fields.Float()
    sum_total_penalty_percentage = fields.Float()
    sum_total_penalty_amount = fields.Float()
    sum_attend_interval = fields.Integer()
    sum_interval_count = fields.Integer()
    sum_absent_interval = fields.Integer()
    sum_absent_penalty_value = fields.Float()
    week_deduction_hours = fields.Float(compute=_compute_week_deduction_hours)
    month_deduction_hours = fields.Float(compute=_compute_month_deduction_hours)
