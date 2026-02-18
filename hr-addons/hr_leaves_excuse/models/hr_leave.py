""" init object hr.leave"""

from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError


# pylint: disable=no-member,too-many-locals
class HrHolidays(models.Model):
    """ init object hr.leave"""
    _inherit = 'hr.leave'

    @api.constrains('leave_category', 'date_from', 'date_to')
    def _check_employee_excuses_hours(self):
        """
        Function  constrains to handle max excuse hours per one times
        """
        if self.leave_category == 'excuse' and \
                self.holiday_status_id and \
                self.holiday_status_id.max_excuse_hours_per_month > 0:
            delta_time = round(
                (self.date_to - self.date_from).total_seconds() / 60) / 60
            if delta_time > self.holiday_status_id.max_excuse_hours_per_month:
                raise UserError(_("You can't exceed  %.2f of Hrs") % self.
                                holiday_status_id.max_excuse_hours_per_month)

    # pylint: disable=translation-positional-used
    def _custom_leave_check(self):
        """
        Override Custom Leave Check only if state is true
        else send the original data of state and response.
        :return: dict {state, response}
        """
        res = super(HrHolidays, self)._custom_leave_check()
        if res.get('state', False):
            self.ensure_one()
            day_start_month = int(self.env['ir.config_parameter'].sudo().
                                  get_param('day_start_month', default="1"))
            max_excuse_hours_per_month = self.holiday_status_id. \
                max_excuse_hours_per_month
            max_excuse_times = self.holiday_status_id.max_excuse_times
            date_from = self.date_from
            day = self.date_from.day
            if day >= day_start_month:
                start_date = datetime(date_from.year, date_from.month,
                                      day_start_month)
            else:
                start_date = datetime(
                    date_from.year,
                    date_from.month,
                    day_start_month
                ) + relativedelta(months=-1)
            end_date = start_date + relativedelta(months=1, seconds=-1)
            # first: Check about count
            domain = [('employee_id', '=', self.employee_id.id),
                      ('holiday_status_id', '=', self.holiday_status_id.id),
                      ('leave_category', '=', "excuse"),
                      ('state', 'in', ['confirm', 'validate', 'validate1']),
                      ('date_from', '>=', str(start_date)),
                      ('date_from', '<=', str(end_date)),
                      ('id', '!=', self.id), ]
            if self.leave_category == 'excuse' and max_excuse_times > 0:
                excuses_count = self.search_count(domain)
                if excuses_count >= max_excuse_times:
                    res['state'] = False
                    response = _("Maximum for excuses per month is %d you "
                                 "already submitted them") % max_excuse_times
                    res['response'] = response
            # Secound: Check about Total Hours
            if self.leave_category == 'excuse' and \
                    max_excuse_hours_per_month > 0:
                leaves = self.search(domain)
                total_leave_hours = 0
                for leave in leaves:
                    date_from = leave.date_from
                    date_to = leave.date_to
                    diff = (date_to - date_from).total_seconds() / 60 / 60
                    total_leave_hours += diff
                diff_time = self.date_to - self.date_from
                this_hours = diff_time.total_seconds() / 60 / 60
                if total_leave_hours + this_hours > max_excuse_hours_per_month:
                    max_per_month = max_excuse_hours_per_month
                    remaining_hur = max_per_month - total_leave_hours
                    res['state'] = False
                    response = _("You have already requested excuses with total"
                                 " %.2f hours and your remaining balance is"
                                 " %.2f hours.") % (total_leave_hours,
                                                    remaining_hur)
                    res['response'] = response
        return res

    @api.constrains('date_from', 'date_to')
    def check_max_excuses(self):
        """
        Function to handle max excuse times between two interval dates
        """
        self.ensure_one()
        res = self._custom_leave_check()
        state = res.get('state', False)
        response = res.get('response', 'done')
        if not state and response:
            raise UserError(response)

    def action_approve(self):
        """
        Override to handle max excuse times between two interval dates
        """
        res = super(HrHolidays, self).action_approve()
        for record in self:
            record.check_max_excuses()
        return res

    def action_confirm(self):
        """
        Override to handle max excuse times between two interval dates
        """
        res = super(HrHolidays, self).action_confirm()
        for record in self:
            record.check_max_excuses()
        return res

    leave_category = fields.Selection(selection_add=[('excuse', 'Excuse')],
                                      ondelete={'excuse': 'set default'})
