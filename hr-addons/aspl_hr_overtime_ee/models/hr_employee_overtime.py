# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

from datetime import date, datetime, timedelta

import pytz
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class hr_employee_overtime(models.Model):
    _name = "hr.employee.overtime"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'HR Employee Overtime'
    _order = 'id desc'

    @api.model
    def _default_employee_id(self):
        return self.env.user.employee_id

    name = fields.Char(string="Name")
    employee_id = fields.Many2one('hr.employee', string="Employee",
                                  default=_default_employee_id)
    manager_id = fields.Many2one(
        'hr.employee',
        related='employee_id.parent_id',
        store=True
    )
    department_id = fields.Many2one(
        'hr.department',
        related='employee_id.department_id',
        store=True
    )
    date = fields.Date(string="Date", default=date.today())
    based_on = fields.Selection([('weekday', 'Weekday'),
                                 ('weekend', 'Weekend')], 'Based On',
                                compute='_compute_based_on', store=True,
                                readonly=False)
    state = fields.Selection([('draft', 'Draft'),
                              ('first_approved', 'First Approved'),
                              ('approved', 'Approved'),
                              ('paid', 'Paid'),
                              ('cancelled', 'Cancelled')], default='draft',
                             string="State", tracking=True)
    ot_rate = fields.Float(string='OT Rate', compute='_get_overtime_rate',
                           store=True,
                           readonly=False)
    overtime = fields.Float(string="Overtime Minute(s)")
    payslip_id = fields.Many2one('hr.payslip', string="Related Payslip")
    allow_approve = fields.Boolean(
        compute='_compute_allow_approve',
    )

    @api.depends('employee_id')
    @api.depends_context('uid')
    def _compute_allow_approve(self):
        """
        get if user is allowed to approve or not
        """
        current_user = self.env.user
        approval_level = self.env['ir.config_parameter'].sudo().get_param(
            'aspl_hr_overtime_ee.ot_approval_level', 'one')
        for record in self:
            overtime_responsible = record.employee_id.overtime_responsible_id
            if record.state == 'draft' and approval_level == 'two' and overtime_responsible == current_user:
                record.allow_approve = True
            elif record.state == 'first_approved' and current_user.has_group(
                    'hr.group_hr_user'):
                record.allow_approve = True
            elif self.env.is_admin():
                record.allow_approve = True
            else:
                record.allow_approve = False

    @api.model
    def create(self, vals):
        ot_name = self.env['ir.sequence'].next_by_code('hr.employee.overtime')
        if ot_name:
            vals.update({'name': ot_name})
        res = super(hr_employee_overtime, self).create(vals)
        for record in res:
            notified_users = record.employee_id.overtime_responsible_id
            approval_level = self.env['ir.config_parameter'].sudo().get_param(
                'aspl_hr_overtime_ee.ot_approval_level', 'one')
            if approval_level == 'one':
                notified_users = self.env.ref('hr.group_hr_user').users
            msg = _(
                'New overtime request need approval %s') % record.display_name
            for user in notified_users:
                record.activity_schedule_with_view(
                    'mail.mail_activity_data_todo',
                    views_or_xmlid='aspl_hr_overtime_ee.aspl_hr_employee_overtime_tree_view',
                    user_id=user.id,
                    summary=msg,
                )
        return res

    def get_date(self, date_time):
        if self._context.get('tz', False):
            tz = pytz.timezone(self._context.get('tz'))
        elif self.env.user.tz:
            tz = pytz.timezone(self.env.user.tz)
        else:
            tz = pytz.utc
        c_time = datetime.now(tz)
        hour_tz = int(str(c_time)[-5:][:2])
        min_tz = int(str(c_time)[-5:][3:])
        sign = str(c_time)[-6][:1]

        if sign == '-':
            date = datetime.strptime(date_time,
                                     "%Y-%m-%d %H:%M:%S") + timedelta(
                hours=hour_tz, minutes=min_tz)
        if sign == '+':
            date = datetime.strptime(date_time,
                                     "%Y-%m-%d %H:%M:%S") - timedelta(
                hours=hour_tz, minutes=min_tz)
        return date

    @api.model
    def generate_employee_overtime(self):
        config_id = self.env['res.config.settings'].search([], limit=1,
                                                           order="id desc")

        for each in self.env['hr.employee'].search([]):
            is_weekday = False
            ot_rate = 0.0
            resource_calendar_id = each.resource_calendar_id if each.resource_calendar_id \
                else config_id.resource_calendar_id if config_id.resource_calendar_id \
                else False

            if resource_calendar_id:
                res_calendar_attendance_id = False
                for each_res_calendar_attendance in resource_calendar_id.attendance_ids:
                    if int(
                            each_res_calendar_attendance.dayofweek) == date.today().weekday():
                        if not res_calendar_attendance_id or \
                                (
                                        res_calendar_attendance_id and res_calendar_attendance_id.hour_to <= each_res_calendar_attendance.hour_to):
                            res_calendar_attendance_id = each_res_calendar_attendance
                        is_weekday = True

                ot_time_difference_limit = config_id.ot_time_difference_limit if config_id and config_id.ot_time_difference_limit else 0.0

                if res_calendar_attendance_id:
                    ot_rate = each.sudo().weekday_ot_rate if each.sudo().weekday_ot_rate \
                        else config_id.sudo().weekday_ot_rate if (
                            config_id and config_id.sudo().weekday_ot_rate) \
                        else 0.0
                else:
                    ot_rate = each.sudo().weekend_ot_rate if each.sudo().weekend_ot_rate \
                        else config_id.sudo().weekend_ot_rate if (
                            config_id and config_id.sudo().weekend_ot_rate) \
                        else 0.0

            hour_to_hr = (str(res_calendar_attendance_id.hour_to).split(".")[
                              0] if '.' in str(
                res_calendar_attendance_id.hour_to) \
                              else str(
                res_calendar_attendance_id.hour_to)) if res_calendar_attendance_id else '00'
            hour_to_minute = (str(int(float(
                str(res_calendar_attendance_id.hour_to).split(".")[
                    1]) * 0.6)) if '.' in str(
                res_calendar_attendance_id.hour_to) \
                                  else '00') if res_calendar_attendance_id else '00'
            date_to_add = datetime.now().replace(hour=int(hour_to_hr),
                                                 minute=int(hour_to_minute),
                                                 second=0)
            if ot_time_difference_limit:
                date_to_add = date_to_add + timedelta(
                    minutes=ot_time_difference_limit)
            date_to_compare = self.get_date(
                str(date_to_add.strftime("%Y-%m-%d %H:%M:%S")))

            if is_weekday:
                attendance_ids = self.env['hr.attendance'].search(
                    [('employee_id', '=', each.id),
                     ('check_out', '>=', str(date_to_compare)),
                     ('check_out', '<=',
                      str(self.get_date(str(date.today()) + " 23:59:59"))),
                     ('employee_ot_id', '=', False)])
            else:
                attendance_ids = self.env['hr.attendance'].search(
                    [('employee_id', '=', each.id),
                     ('check_out', '>=',
                      str(self.get_date(str(date.today()) + " 00:00:00"))),
                     ('check_out', '<=',
                      str(self.get_date(str(date.today()) + " 23:59:59"))),
                     ('employee_ot_id', '=', False)])

            overtime = 0.0
            for each_attendance_id in attendance_ids:
                if is_weekday:
                    date1 = date_to_compare if date_to_compare > fields.Datetime.from_string(
                        each_attendance_id.check_in) \
                        else fields.Datetime.from_string(
                        each_attendance_id.check_in)
                else:
                    date1 = fields.Datetime.from_string(
                        each_attendance_id.check_in)
                date2 = fields.Datetime.from_string(
                    each_attendance_id.check_out)
                duration = (date2 - date1).total_seconds()
                overtime += divmod(duration, 60)[0]

            if overtime and ot_rate:
                employee_ot_id = self.env['hr.employee.overtime'].create({
                    'employee_id': each.id,
                    'date': date.today(),
                    'based_on': 'weekday' if is_weekday else 'weekend',
                    'ot_rate': ot_rate,
                    'overtime': overtime
                })

                attendance_ids.update({'employee_ot_id': employee_ot_id.id})

    def emp_overtime_approve(self):
        self.ensure_one()
        approval_level = self.env['ir.config_parameter'].sudo().get_param(
            'aspl_hr_overtime_ee.ot_approval_level', 'one')
        if self.state == 'draft' and approval_level == 'two':
            responsible_user = self.employee_id.sudo().overtime_responsible_id
            if not responsible_user and not self.env.is_admin():
                raise UserError(
                    _('Please assign overtime responsible for employee!'))
            if responsible_user != self.env.user and not self.env.is_admin():
                raise UserError(_(
                    'Please contact %s for first approval') % responsible_user.display_name)

            self.state = 'first_approved'
            msg = _('Overtime request need approval %s') % self.display_name
            notified_users = self.env.ref('hr.group_hr_user').users
            for user in notified_users:
                self.activity_schedule_with_view(
                    'mail.mail_activity_data_todo',
                    views_or_xmlid='aspl_hr_overtime_ee.aspl_hr_employee_overtime_tree_view',
                    user_id=user.id,
                    summary=msg,
                )
            return True
        attendance_ids = self.env['hr.attendance'].search(
            [('employee_id', '=', self.employee_id.id),
             ('check_out', '>=',
              str(self.date) + " 00:00:00"),
             ('check_out', '<=',
              str(self.date) + " 23:59:59"),
             ('employee_ot_id', '=', False)])
        if attendance_ids:
            attendance_ids.write({'employee_ot_id': self.id})
        self.state = 'approved'

    def emp_overtime_cancel(self):
        self.ensure_one()
        attendance_ids = self.env['hr.attendance'].search(
            [('employee_ot_id', '=', self.id)])
        if attendance_ids:
            attendance_ids.update({'employee_ot_id': False})
        self.state = 'cancelled'

    @api.depends('date', 'employee_id')
    def _compute_based_on(self):
        config_id = self.env['res.config.settings'].search([], limit=1,
                                                           order="id desc")
        for record in self:
            employee_id = record.employee_id
            overtime_date = record.date
            is_weekday = False
            if employee_id and overtime_date:
                resource_calendar_id = employee_id.resource_calendar_id if employee_id.resource_calendar_id \
                    else config_id.resource_calendar_id if config_id.resource_calendar_id \
                    else False
                if resource_calendar_id:
                    res_calendar_attendance_id = False
                    for each_res_calendar_attendance in resource_calendar_id.attendance_ids:
                        if int(
                                each_res_calendar_attendance.dayofweek) == overtime_date.weekday():
                            if not res_calendar_attendance_id or \
                                    (
                                            res_calendar_attendance_id and res_calendar_attendance_id.hour_to <= each_res_calendar_attendance.hour_to):
                                res_calendar_attendance_id = each_res_calendar_attendance
                            is_weekday = True
            record.based_on = 'weekday' if is_weekday else 'weekend'

    @api.depends('date', 'employee_id', 'based_on')
    def _get_overtime_rate(self):
        config_id = self.env['res.config.settings'].search([], limit=1,
                                                           order="id desc")
        for record in self:
            employee_id = record.employee_id
            overtime_date = record.date
            based_on = record.based_on
            ot_rate = 0.0
            if employee_id and overtime_date and based_on:
                if based_on == 'weekday':
                    ot_rate = employee_id.sudo().weekday_ot_rate if employee_id.sudo().weekday_ot_rate \
                        else config_id.sudo().weekday_ot_rate if (
                            config_id and config_id.sudo().weekday_ot_rate) \
                        else 0.0
                if based_on == 'weekend':
                    ot_rate = employee_id.sudo().weekend_ot_rate if employee_id.sudo().weekend_ot_rate \
                        else config_id.sudo().weekend_ot_rate if (
                            config_id and config_id.sudo().weekend_ot_rate) \
                        else 0.0
            record.ot_rate = ot_rate

    @api.constrains('overtime')
    def _constrain_overtime(self):
        if self.filtered(lambda e: e.overtime == 0.0):
            raise UserError(_("Please specify overtime minutes for request"))
