""" init object resource.calendar to fix odoo """

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ResourceCalendar(models.Model):
    """ init object resource.calendar to fix odoo """

    _inherit = 'resource.calendar'

    @api.constrains('absent_deduction_value_per_day')
    def _constrains_absent_deduction_value_per_day(self):
        """
        Constrains absent_deduction_value_per_day.
        """
        for rec in self:
            if rec.absent_deduction_value_per_day < 0.0:
                raise UserError(_("Absent Deduction Value Per Interval"
                                  "Must Be Positive."))

    @api.constrains('maximum_deduction_per_day')
    def _constrains_maximum_deduction_per_day(self):
        """
        Constrains maximum_deduction_per_day.
        """
        for rec in self:
            if rec.maximum_deduction_per_day < 0.0:
                raise UserError(_("Maximum Penalty Per Day Must Be Positive."))

    # pylint: disable=too-many-locals,no-self-use
    @api.model
    def get_h_m_midday(self, midday_time):
        """
        Get Hours and Minutes from Midday Float Time.
        :param midday_time:
        :return:midday_time_h, midday_time_m
        """
        midday_time_h = int(midday_time)
        midday_time_m = int(
            round(((midday_time - midday_time_h) * 60), 0))
        return midday_time_h, midday_time_m

    # pylint: disable=too-many-locals,no-member, invalid-name
    # pylint: disable=unused-argument, too-many-arguments
    def _attendance_intervals(self, start_dt, end_dt, resource=None,
                              domain=None, tz=None):
        """
        Override Get Intervals to handel flexible.
        :param start_dt:
        :param end_dt:
        :param resource:
        :param domain:
        :param tz:
        :return: intervals
        """
        # intervals = super(ResourceCalendar, self)._attendance_intervals(
        #     start_dt, end_dt, resource=resource)
        
        if resource is None:
            resource = self.env['resource.resource']
        intervals = super(ResourceCalendar, self)._attendance_intervals_batch(
            start_dt, end_dt, resources=resource, domain=domain, tz=tz
             )[resource.id]
        
        ctx = self.env.context.copy()
        if 'compute_attendance' not in ctx:
            return intervals
        new_intervals = []
        if self.is_flexible and intervals:
            midday_time = round(
                float(self.env['ir.config_parameter'].sudo()
                      .get_param('midday_time', default=0.0)),
                2
            )

            for interval_id in intervals:
                d_from = old_from = interval_id[0]
                d_to = old_to = interval_id[1]
                rc_attendance_id = interval_id[2]
                flexible_id = rc_attendance_id.flexible_id
                if flexible_id \
                        and flexible_id.allow_attend_before_schedule \
                        and old_from:
                    if not flexible_id.allowed_from_midday \
                            and flexible_id.allowed_from:
                        time_h, time_m = self.get_h_m_midday(
                            flexible_id.allowed_from)
                    else:
                        time_h, time_m = self.get_h_m_midday(midday_time)
                    d_from = old_from.replace(hour=time_h, minute=time_m,
                                              second=0)
                if flexible_id \
                        and flexible_id.allow_attend_after_schedule \
                        and old_from:
                    if not flexible_id.allowed_to_midday \
                            and flexible_id.allowed_to:
                        time_h, time_m = self.get_h_m_midday(
                            flexible_id.allowed_to)
                        d_to = old_from.replace(hour=time_h, minute=time_m,
                                                second=0)
                    else:
                        time_h, time_m = self.get_h_m_midday(midday_time)
                        temp_from = old_from.replace(hour=time_h, minute=time_m,
                                                     second=0)
                        d_to = (temp_from + relativedelta(days=1, seconds=-1))

                if d_from not in [rec[0] for rec in new_intervals] \
                        and d_to not in [rec[1] for rec in new_intervals]:
                    new_intervals.append((old_from, old_to, rc_attendance_id,
                                          d_from, d_to,))
            return new_intervals

        for interval_id in intervals:
            d_from = interval_id[0]
            d_to = interval_id[1]
            rc_attendance_id = interval_id[2]
            new_intervals.append((d_from, d_to, rc_attendance_id,
                                  d_from, d_to,))
        return new_intervals

    penalty_ids = fields.One2many(comodel_name="hr.penalty.rule",
                                  inverse_name="calendar_id",
                                  string="Penalty Rules", required=False)
    absent_ids = fields.One2many(comodel_name="hr.absent.penalty.rule",
                                 inverse_name="calendar_id",
                                 string="Absent Penalties", required=False)
    is_flexible = fields.Boolean()
    absent_deduction_value_per_day = fields.Float(
        string="Maximum Absent Deduction Value Per Day",
        required=False, default=1,
    )
    maximum_deduction_per_day = fields.Float(
        string="Maximum Penalty Per Day (For Deduction Percentage only)",
        required=True, default=1,
    )
