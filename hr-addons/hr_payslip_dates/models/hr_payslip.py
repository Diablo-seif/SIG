""" Update object hr.payslip """

from datetime import datetime, date, time

import babel
from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models, tools


class HrPayslip(models.Model):
    """ Update object hr.payslip """
    _inherit = "hr.payslip"

    # pylint: disable=no-member, attribute-defined-outside-init
    @api.onchange('employee_id', 'struct_id', 'contract_id', 'date_from',
                  'date_to')
    def _onchange_employee(self):
        """
        Overrider Onchange Employee or date_from or date_to
        """
        res = super(HrPayslip, self)._onchange_employee()
        self.name = self.get_default_name(self.date_from,
                                          self.employee_id.id)
        return res

    # pylint: disable=no-member
    def onchange_employee_id(self, date_from, date_to, employee_id=False,
                             contract_id=False):
        """
        Override onchange_employee_id
        :param date_from:
        :param date_to:
        :param employee_id:
        :param contract_id:
        :return:
        """
        res = super(HrPayslip, self).onchange_employee_id(date_from, date_to,
                                                          employee_id,
                                                          contract_id)
        res['value']['name'] = self.get_default_name(date_from, employee_id)
        return res

    def get_default_name(self, chosen_date, employee_id):
        """Get default payslip name.

        Return payslip name with current month instead of previous month."""
        month_date = chosen_date
        # fetch configuration from system parameters
        conf_sudo = self.env['ir.config_parameter'].sudo()
        day_start_month = int(conf_sudo.get_param('day_start_month',
                                                  default="1")) or 1
        start_month_conf = conf_sudo.get_param('start_month',
                                               default="current")
        employee = self.env['hr.employee'].browse(employee_id)
        # if start date changed from the configured option, use the default
        # behavior
        if chosen_date.day == day_start_month \
                and start_month_conf == 'previous':
            month_date = chosen_date + relativedelta(months=1)
        ttyme = datetime.combine(fields.Date.from_string(month_date),
                                 time.min)
        locale = self.env.context.get('lang') or 'en_US'
        format_date = tools.ustr(babel.dates.format_date(
            date=ttyme, format='MMMM-y', locale=locale))
        name = _('Salary Slip of %(employee_name)s '
                 'for %(date)s') % {
                     "employee_name": employee.name,
                     "date": format_date
                 }
        return name

    def get_default_dates(self):
        """
        Get Default Dates
        :return: list [date_from, date_to]
        """
        # default date
        date_now = date.today()

        # fetch configuration from system parameters
        conf_sudo = self.env['ir.config_parameter'].sudo()
        day_start_month = int(conf_sudo.get_param('day_start_month',
                                                  default="1")) or 1
        start_month_conf = conf_sudo.get_param('start_month',
                                               default="current")
        months = -1 if start_month_conf == 'previous' else 0

        # set start and end date as offsets from the chosen date
        start_date = date(date_now.year, date_now.month,
                          day_start_month) + relativedelta(months=months)
        end_date = start_date + relativedelta(months=1, days=-1)
        return [start_date, end_date]

    def _get_default_date_from(self):
        """
        Get Default Date From.
        :return: date_from <date>
        """
        date_list = self.get_default_dates()
        if date_list:
            return date_list[0]
        return fields.Date.to_string(date.today().replace(day=1))

    def _get_default_date_to(self):
        """
        Get Default Date To.
        :return: date_to <date>
        """
        date_list = self.get_default_dates()
        if date_list:
            return date_list[1]
        return fields.Date.to_string(
            (datetime.now() + relativedelta(months=+1, day=1,
                                            days=-1)).date())

    date_from = fields.Date(default=_get_default_date_from)
    date_to = fields.Date(default=_get_default_date_to)
