""" init object hr.attendance.record """

import logging
from datetime import datetime

import pytz
from dateutil.relativedelta import relativedelta
from odoo.addons.resource.models.resource import Intervals

from odoo import _, api, fields, models
from odoo.exceptions import UserError

LOGGER = logging.getLogger(__name__)
UTC_TZ = pytz.timezone('UTC')


# pylint: disable=no-member,unused-argument,no-self-use,too-many-branches
class HrAttendanceRecord(models.Model):
    """ init object hr.attendance.record """
    _name = 'hr.attendance.record'
    _description = 'HR Attendance Record'
    _order = 'date desc, employee_id desc'
    _inherit = ['mail.thread']

    def name_get(self):
        """
        Override Name Get.
        """
        res = []
        for rec in self:
            dis_name = "Employee:%s Day:%s Date:%s" \
                       "" % (rec.employee_id.name,
                             rec.name,
                             rec.date)
            res.append((rec.id, dis_name))
        return res

    @api.depends('date')
    def _compute_name(self):
        """
        Compute Name Of Day.
        """
        for rec in self:
            if rec.date:
                rec.name = rec.date.strftime('%A')
            else:
                rec.name = False

    # pylint: disable=invalid-name, protected-access
    def _get_list_related_dates(self, start_datetime,
                                end_datetime):
        """
        Get List Attendance and leaves Related To Dates.
        :param start_interval_datetime:
        :param end_interval_datetime:
        :return all_intervals_list: <Intervals>
        """
        attend_ids = self.env['hr.attendance'].search(
            [('employee_id', '=', self.employee_id.id),
             ('check_in', '<=', end_datetime),
             ('check_out', '>=', start_datetime)],
            order='check_in desc'
        )
        obj = self.env['hr.compute.attendance']
        all_intervals_list = []
        for attend_id in attend_ids:
            elm_0 = attend_id.check_in.replace(tzinfo=UTC_TZ)
            elm_1 = attend_id.check_out.replace(tzinfo=UTC_TZ)
            all_intervals_list.append((max(start_datetime, elm_0),
                                       min(end_datetime, elm_1), obj))
        interval_leave_list = self.resource_calendar_id._leave_intervals(
            start_datetime, end_datetime, self.employee_id.resource_id)
        for one_leave in interval_leave_list:
            all_intervals_list.append((one_leave[0], one_leave[1], obj))
        all_intervals_list.sort()

        res_intervals = Intervals(all_intervals_list)
        if not res_intervals:
            return []
        return res_intervals._items

    def _get_delay_in(self, start_interval_datetime, all_intervals_list):
        """
        Get Delay In Minutes.
        :param start_interval_datetime:
        :param all_intervals_list:
        :return: delay_in <integer> Minutes.
        """
        self.ensure_one()
        first_datetime = None
        if all_intervals_list:
            first_record = all_intervals_list[0]
            if first_record:
                first_datetime = first_record[0]
        if first_datetime and first_datetime > start_interval_datetime:
            diff = first_datetime - start_interval_datetime
            return diff.seconds / 60
        return 0

    def _get_actual_working_hours(self, allow_from_datetime,
                                  allow_to_datetime):
        """
        Get actual_working_hours.
        :param allow_from_datetime:
        :param allow_to_datetime:
        :return: <Float> actual_working_hours
        """
        allow_intervals_list = self._get_list_related_dates(
            allow_from_datetime, allow_to_datetime)
        total_seconds = 0
        for item in allow_intervals_list:
            total_seconds += (item[1] - item[0]).total_seconds()
        actual_working_hours = total_seconds / 60 / 60
        return actual_working_hours

    def _get_early_out(self, end_interval_datetime, all_intervals_list):
        """
        Get Early Out Minutes.
        :param end_interval_datetime:
        :param all_intervals_list:
        :return: early_out <integer> Minutes.
        """
        last_datetime = None
        if all_intervals_list:
            last_record = all_intervals_list[-1]
            last_datetime = last_record[1]
        if last_datetime and end_interval_datetime > last_datetime:
            diff = end_interval_datetime - last_datetime
            return diff.seconds / 60
        return 0

    def _get_total_missing_seconds(self, start_interval, end_interval,
                                   all_intervals_list):
        """
        Get Total Missing Seconds.
        :param start_interval:datetime
        :param end_interval:datetime
        :param all_intervals_list: (start datetime, end datetime, obj)
        :return: Total Seconds Integer.
        """
        total_seconds = 0
        if not all_intervals_list:
            return total_seconds
        intervals = all_intervals_list
        intervals = sorted(intervals, key=lambda tup: tup[0])
        current_datetime = start_interval
        while intervals:
            if intervals[0][0] > current_datetime:
                diff = intervals[0][0] - current_datetime
                total_seconds += diff.total_seconds()
            current_datetime = intervals[0][1]
            intervals.pop(0)
        if end_interval > current_datetime:
            diff = end_interval - current_datetime
            total_seconds += diff.total_seconds()
        return total_seconds

    def _write_update_record(self, values):
        """
        Update Final per day Record.
        """
        keys_for_pop = []
        for key, value in values.items():
            if not value:
                keys_for_pop.append(key)
        for key in keys_for_pop:
            values.pop(key)
        self.update(values)

    # pylint: disable=too-many-locals, too-many-statements

    def update_record(self):
        """
        Main Function To Compute Per Day Record.
        """
        self.ensure_one()
        ctx = self.env.context.copy()
        ctx.update(compute_attendance=True)
        midday_time = round(
            float(self.env['ir.config_parameter'].sudo()
                  .get_param('midday_time', default=0.0)),
            2
        )
        within_contract_duration = True
        missing_without_delay_in = False
        missing_without_early_out = False
        missing_without_delay_in_str = self.env['ir.config_parameter'].sudo(). \
            get_param('missing_without_delay_in', default="false")
        missing_without_early_out_str = self.env['ir.config_parameter']. \
            sudo().get_param('missing_without_early_out', default="false")
        if missing_without_delay_in_str in ["true", "True", "1"]:
            missing_without_delay_in = True
        if missing_without_early_out_str in ["true", "True", "1"]:
            missing_without_early_out = True
        midday_time_h = int(midday_time)
        midday_time_m = round(((midday_time - midday_time_h) * 60), 0)
        date = self.date
        date_from_datetime = datetime(date.year, date.month, date.day,
                                      int(midday_time_h), int(midday_time_m),
                                      0).replace(tzinfo=UTC_TZ)
        date_to_datetime = (date_from_datetime + relativedelta(days=1,
                                                               seconds=-1))
        self.contract_id = self.env['hr.contract'].search(
            [('employee_id', '=', self.employee_id.id),
             ('date_start', '<=', self.date),
             ('state', 'not in', ['draft', 'cancel'])],
            order='date_start desc',
            limit=1)
        if self.contract_id \
                and self.contract_id.date_end \
                and self.contract_id.date_end < self.date:
            within_contract_duration = False
        if not self.employee_id.resource_id:
            raise UserError(_(
                "Error !! Cannot Fined `resource_id` For Employee: %s"
            ) % self.employee_id.name)
        resource_id = self.employee_id.resource_id
        if not self.contract_id:
            # get current contract for new employees
            self.contract_id = self.employee_id.contract_id
            within_contract_duration = False
        if not self.contract_id:
            raise UserError(_(
                "You Cannot Compute Attendance For Employee: %(employee_name)s"
                " Without Contract Duration In %(date)s."
            ) % {"employee_name": self.employee_id.name,
                 "date": fields.Date.to_string(self.date)})
        date_from_str = fields.Datetime.to_string(date_from_datetime)
        date_to_str = fields.Datetime.to_string(date_to_datetime)
        if not self.resource_calendar_id:
            raise UserError(_(
                "You Cannot Compute Attendance For Employee: %s"
                " Not Assigned to Work Schedule."
            ) % self.employee_id.name)
        attendance_ids = self.env['hr.attendance'].search(
            [('employee_id', '=', self.employee_id.id),
             ('check_in', '<=', date_to_str),
             ('check_out', '>=', date_from_str)], order='check_in desc'
        )
        leave_ids = self.env['resource.calendar.leaves'].search(
            ['|',
             ('resource_id', '=', resource_id.id),
             ('resource_id', '=', False),
             ('date_from', '<=', date_to_str),
             ('date_to', '>=', date_from_str)], order='date_from desc'
        )
        
        # pylint: disable=protected-access
        intervals = self.resource_calendar_id.with_context(
            **ctx)._attendance_intervals(date_from_datetime, date_to_datetime)

        interval_ids = self.env['hr.attendance.interval']
        for interval in intervals:
            start_interval = interval[0].astimezone(UTC_TZ)
            end_interval = interval[1].astimezone(UTC_TZ)
            rc_attendance_id = interval[2]
            allow_form_datetime = interval[3].astimezone(UTC_TZ)
            allow_to_datetime = interval[4].astimezone(UTC_TZ)
            all_intervals_list = self._get_list_related_dates(start_interval,
                                                              end_interval)
            is_attend = False
            if all_intervals_list:
                is_attend = True
            delay_in = self._get_delay_in(start_interval, all_intervals_list)
            early_out = self._get_early_out(end_interval, all_intervals_list)
            total_missing_seconds = self._get_total_missing_seconds(
                start_interval, end_interval, all_intervals_list)
            missing_mints = total_missing_seconds / 60
            if missing_without_delay_in:
                missing_mints -= delay_in
            if missing_without_early_out:
                missing_mints -= early_out
            missing_hours = missing_mints / 60
            working_hours = rc_attendance_id.hour_to - rc_attendance_id. \
                hour_from
            min_hours_attend = working_hours
            if self.resource_calendar_id.is_flexible \
                    and rc_attendance_id.flexible_id \
                    and rc_attendance_id.flexible_id.day_hours:
                min_hours_attend = rc_attendance_id.flexible_id.day_hours
            actual_working_hours = self._get_actual_working_hours(
                allow_form_datetime, allow_to_datetime)
            if self.resource_calendar_id.is_flexible:
                missing_hours = 0
                if min_hours_attend > actual_working_hours:
                    missing_hours = min_hours_attend - actual_working_hours
            if missing_hours < 0:
                missing_hours = 0.0
            if not is_attend:
                missing_hours = 0.0
            vals = {
                'name': str(interval) or "None",
                'record_id': self.id,
                'is_attend': is_attend,
                'delay_in': int(delay_in),
                'early_out': int(early_out),
                'working_hours': working_hours,
                'min_hours_attend': min_hours_attend,
                'missing_hours': missing_hours,
                'actual_working_hours': actual_working_hours,
                'start_datetime': fields.Datetime.to_string(start_interval),
                'end_datetime': fields.Datetime.to_string(end_interval),
                'allow_form_datetime': fields.Datetime.to_string(
                    allow_form_datetime),
                'allow_to_datetime': fields.Datetime.to_string(
                    allow_to_datetime),
            }
            interval_id = self.env['hr.attendance.interval'].create(vals)
            if within_contract_duration:
                interval_ids |= interval_id
            attendance_ids |= attendance_ids
            self._write_update_record({
                'interval_ids': interval_ids,
                'within_contract_duration': within_contract_duration,
                'attendance_ids': attendance_ids,
                'leave_ids': leave_ids
            })
            msg = "Update Record:%s | %s -> %s | %s to %s." \
                  "" % (self.employee_id.name, self.name, self.date,
                        date_from_str,
                        date_to_str)
            LOGGER.info(msg)

    @api.depends('interval_ids', 'interval_ids.penalty_in_percentage',
                 'interval_ids.penalty_in_amount',
                 'interval_ids.penalty_out_percentage',
                 'interval_ids.penalty_out_amount',
                 'interval_ids.penalty_missing_percentage',
                 'interval_ids.penalty_missing_amount',
                 'resource_calendar_id.maximum_deduction_per_day')
    def _compute_total_penalty(self):
        """
        Compute Total Penalty Value With Maximum Configuration.
        :return:
        """
        for rec in self:
            maximum_deduction_percentage = rec.resource_calendar_id. \
                maximum_deduction_per_day
            total_penalty_in_percentage = 0.0
            total_penalty_out_percentage = 0.0
            total_penalty_missing_percentage = 0.0
            total_penalty_in_amount = 0.0
            total_penalty_out_amount = 0.0
            total_penalty_missing_amount = 0.0
            for interval_id in rec.interval_ids:
                total_penalty_in_percentage += interval_id.penalty_in_percentage
                total_penalty_out_percentage += \
                    interval_id.penalty_out_percentage
                total_penalty_missing_percentage += \
                    interval_id.penalty_missing_percentage
                total_penalty_in_amount += interval_id.penalty_in_amount
                total_penalty_out_amount += interval_id.penalty_out_amount
                total_penalty_missing_amount += \
                    interval_id.penalty_missing_amount

            total_in_out_percentage = \
                total_penalty_in_percentage + total_penalty_out_percentage
            total_penalties_percentage = \
                total_in_out_percentage + total_penalty_missing_percentage
            total_in_out_amount = \
                total_penalty_in_amount + total_penalty_out_amount
            rec.total_penalty_amount = \
                total_in_out_amount + total_penalty_missing_amount
            if total_penalties_percentage >= maximum_deduction_percentage:
                rec.total_penalty_percentage = maximum_deduction_percentage
            else:
                rec.total_penalty_percentage = total_penalties_percentage

    @api.depends('interval_ids', 'interval_ids.is_attend')
    def _compute_absent_interval(self):
        """
        Compute absent interval.
        """
        for rec in self:
            absent_interval = 0
            for interval_id in rec.interval_ids:
                if not interval_id.is_attend:
                    absent_interval += 1
            rec.absent_interval = absent_interval

    @api.depends('interval_ids', 'interval_ids.is_attend')
    def _compute_attend_interval(self):
        """
        Compute interval attend.
        """
        for rec in self:
            attend_interval = 0
            for interval_id in rec.interval_ids:
                if interval_id.is_attend:
                    attend_interval += 1
            rec.attend_interval = attend_interval

    @api.depends('interval_ids')
    def _compute_interval_count(self):
        """
        Compute interval Count.
        """
        for rec in self:
            rec.interval_count = len(rec.interval_ids)

    @api.depends('interval_ids', 'interval_ids.working_hours')
    def _compute_working_schedule_hours(self):
        """
        Compute working_schedule_hours.
        """
        for rec in self:
            working_schedule_hours = 0
            for interval_id in rec.interval_ids:
                working_schedule_hours += interval_id.working_hours
            rec.working_schedule_hours = working_schedule_hours

    @api.depends('interval_ids', 'interval_ids.actual_working_hours',
                 'interval_ids.missing_hours')
    def _compute_total_actual_working_hours(self):
        """
        Compute actual_working_hours.
        """
        for rec in self:
            total_actual_working_hours = 0
            for interval_id in rec.interval_ids:
                total_actual_working_hours += interval_id.actual_working_hours
            rec.total_actual_working_hours = total_actual_working_hours

    @api.depends('interval_ids', 'interval_ids.missing_hours')
    def _compute_total_missing_hours(self):
        """
        Compute total_missing_hours.
        """
        for rec in self:
            total_missing_hours = 0
            for interval_id in rec.interval_ids:
                total_missing_hours += interval_id.missing_hours
            rec.total_missing_hours = total_missing_hours

    @api.depends('interval_ids', 'interval_ids.absent_value',
                 'resource_calendar_id.absent_deduction_value_per_day')
    def _compute_absent_penalty_value(self):
        """
        Compute absent_penalty_value.
        """
        for rec in self:
            maximum_absent = rec.resource_calendar_id. \
                absent_deduction_value_per_day
            absent_penalty_value = 0
            for interval_id in rec.interval_ids:
                absent_penalty_value += interval_id.absent_value
            if maximum_absent and absent_penalty_value > maximum_absent:
                absent_penalty_value = maximum_absent
            rec.absent_penalty_value = absent_penalty_value

    @api.depends('interval_ids', 'interval_ids.working_hours',
                 'interval_ids.is_attend')
    def _compute_must_attend_hours(self):
        """
        Compute must_attend_hours.
        """
        for rec in self:
            must_attend_hours = 0
            for interval_id in rec.interval_ids.filtered(
                    lambda interval: interval.is_attend):
                must_attend_hours += interval_id.working_hours
            rec.must_attend_hours = must_attend_hours

    name = fields.Char(string="Day", compute=_compute_name, store=True)
    date = fields.Date(required=True)
    weekday = fields.Char()
    month = fields.Char()
    employee_id = fields.Many2one(comodel_name="hr.employee", required=True)
    contract_id = fields.Many2one(comodel_name="hr.contract")
    attendance_ids = fields.Many2many(comodel_name="hr.attendance",
                                      relation="compute_attendance_rel",
                                      column1="compute_id",
                                      column2="attendance_id",
                                      string="Attendances")
    interval_ids = fields.Many2many(comodel_name="hr.attendance.interval",
                                    relation="compute_interval_rel",
                                    column1="compute_id",
                                    column2="interval_id",
                                    string="Intervals")
    resource_calendar_id = fields.Many2one(
        'resource.calendar',
        'Working Schedule',
        related='contract_id.resource_calendar_id',
        store=True,
    )
    working_schedule_hours = fields.Float(
        compute=_compute_working_schedule_hours, store=True,
    )
    must_attend_hours = fields.Float(
        compute=_compute_must_attend_hours, store=True,
    )
    total_actual_working_hours = fields.Float(
        compute=_compute_total_actual_working_hours, store=True,
    )
    total_missing_hours = fields.Float(
        compute=_compute_total_missing_hours, store=True,
    )
    total_penalty_percentage = fields.Float(compute=_compute_total_penalty,
                                            store=True)
    total_penalty_amount = fields.Float(compute=_compute_total_penalty,
                                        store=True)
    attend_interval = fields.Integer(compute=_compute_attend_interval,
                                     store=True)
    interval_count = fields.Integer(compute=_compute_interval_count, store=True)
    absent_interval = fields.Integer(compute=_compute_absent_interval,
                                     store=True)
    absent_penalty_value = fields.Float(
        compute=_compute_absent_penalty_value, store=True,
    )
    leave_ids = fields.Many2many(comodel_name="resource.calendar.leaves",
                                 relation="compute_resource_leave_rel",
                                 column1="compute_id",
                                 column2="resource_leave_id",
                                 string="Resource Leaves")
    within_contract_duration = fields.Boolean()
