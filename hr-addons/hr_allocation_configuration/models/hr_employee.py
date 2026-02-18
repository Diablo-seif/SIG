""" HR Employee """

from dateutil.relativedelta import relativedelta

from odoo import SUPERUSER_ID, _, api, fields, models


# pylint: disable=protected-access
class HrEmployee(models.Model):
    """ inherit HR Employee """
    _inherit = 'hr.employee'

    insurance_checked = fields.Boolean(groups="hr.group_hr_user")
    total_insurance_years = fields.Integer(
        groups="hr.group_hr_user",
        compute='_compute_total_insurance_years', store=True
    )

    @api.depends('insurance_history_ids.insurance_days')
    def _compute_total_insurance_years(self):
        """ Compute total_insurance_years value """
        for rec in self:
            rec.total_insurance_years = sum(
                rec.mapped('insurance_history_ids.insurance_days')
            ) / 365

    @api.model
    def check_employee_insurance(self):
        """ check employee insurance """
        cfg_age = self.env.company.time_off_employee_age
        cfg_insurance = self.env.company.time_off_years_of_insurance
        employees = self.search([('insurance_checked', '=', False)])
        for employee in employees:
            emp_age = relativedelta(
                fields.date.today(), (employee.birthday or fields.date.today())
            ).years
            user_id = employee.leave_manager_id.id or SUPERUSER_ID
            if emp_age >= cfg_age:
                employee._activity_schedule_with_view(
                    'mail.mail_activity_data_todo',
                    views_or_xmlid='hr.view_employee_tree',
                    user_id=user_id,
                    summary=_('%(employee_name)s Age exceeded %(cfg_age)s '
                              'years') % {
                                  "employee_name": employee.name,
                                  "cfg_age": cfg_age
                              }
                )
                employee.insurance_checked = True
            if employee.total_insurance_years >= cfg_insurance:
                employee._activity_schedule_with_view(
                    'mail.mail_activity_data_todo',
                    views_or_xmlid='hr.view_employee_tree',
                    user_id=user_id,
                    summary=_('%(employee_name)s Insurance exceeded '
                              '%(cfg_insurance)s years') % {
                                  "employee_name": employee.name,
                                  "cfg_insurance": cfg_insurance
                              }
                )
                employee.insurance_checked = True
