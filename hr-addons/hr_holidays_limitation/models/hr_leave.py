""" HR Leave """
from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HrLeave(models.Model):
    """ inherit HR Leave to add limitation constrains"""
    _inherit = 'hr.leave'

    @api.constrains('holiday_status_id', 'date_from', 'request_date_from')
    def _check_limitation(self):
        """
        check that user cannot request time off before limitation
        """
        if self.user_has_groups('!hr_holidays.group_hr_holidays_manager'):
            timezone = self.with_context(
                tz=self._context.get('tz') or
                self.env.user.partner_id.tz or 'UTC'
            )
            for leave in self:
                if leave.leave_type_request_unit == 'day' and \
                        leave.holiday_status_id.no_of_days:
                    limited_date = fields.Date.today() + relativedelta(
                        days=leave.holiday_status_id.no_of_days)
                    if leave.request_date_from and \
                            leave.request_date_from < limited_date:
                        raise ValidationError(
                            _('The %(type_name)s must be requested at least '
                              '%(number_days)s day(s) '
                              'before the desired date') % {
                                  "type_name": leave.holiday_status_id.name,
                                  "number_days":
                                      leave.holiday_status_id.no_of_days
                              }
                        )
                else:
                    if leave.holiday_status_id.no_of_hours:
                        date_from = fields.Datetime.context_timestamp(
                            timezone, leave.date_from
                        ).replace(tzinfo=None)
                        limited_time = fields.Datetime.context_timestamp(
                            timezone, (fields.Datetime.now() + relativedelta(
                                hours=leave.holiday_status_id.no_of_hours))
                        ).replace(tzinfo=None)
                        if date_from < limited_time:
                            raise ValidationError(
                                _('The %(type_name)s must be requested '
                                  'at least %(number_hours)s hour(s) '
                                  'before the desired hours') % {
                                      "type_name": leave.holiday_status_id.name,
                                      "number_hours":
                                          leave.holiday_status_id.no_of_hours
                                  }
                            )
                contract = leave.sudo().employee_id.contract_id
                if contract.date_start and leave.request_date_from:
                    contract_limitation = contract.date_start + relativedelta(
                        days=leave.holiday_status_id.contract_limitation)
                    if leave.request_date_from < contract_limitation and \
                            contract.time_off_limitation:
                        raise ValidationError(
                            _('%s day(s) should pass from contract '
                              'start date to request a time off') % (
                                  leave.holiday_status_id.contract_limitation
                              )
                        )
