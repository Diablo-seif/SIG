""" Employee Insurance History """

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class EmployeeInsuranceHistory(models.Model):
    """ Employee Insurance History """
    _name = 'employee.insurance.history'
    _description = 'Employee Insurance History'
    _sql_constraints = [
        ('date_check',
         'CHECK ((date_from <= date_to))',
         'Start date must be anterior to the end date.'),
        ('date_from_check',
         'CHECK ((date_from <= CURRENT_DATE))',
         'Start date cannot be after current date.'),
    ]

    employee_id = fields.Many2one(
        'hr.employee'
    )
    company = fields.Char(
        required=True
    )
    date_from = fields.Date(
        required=True
    )
    date_to = fields.Date()
    duration_days = fields.Integer(
        compute='_compute_duration',
        string='Days'
    )
    duration_months = fields.Integer(
        compute='_compute_duration',
        string='Months'
    )
    duration_years = fields.Integer(
        compute='_compute_duration',
        string='Years'
    )
    insurance_days = fields.Integer(
        compute='_compute_duration'
    )
    insurance_salary = fields.Monetary()
    basic_salary = fields.Monetary()
    variable_salary = fields.Monetary()
    currency_id = fields.Many2one(
        'res.currency',
        related="employee_id.currency_id",
        store=True
    )

    @api.constrains('insurance_salary')
    def _check_insurance_salary(self):
        """ Validate insurance_salary """
        for rec in self:
            config = self.env['social.insurance.config'].search([
                '|',
                ('date_from', '=', False),
                ('date_from', '<=', rec.date_from),
                '|',
                ('date_to', '=', False),
                ('date_to', '>=', rec.date_from)

            ], limit=1)
            if not config:
                return
            # @formatter:off
            if (config.min_value and
                    rec.insurance_salary < config.min_value) or \
                    (config.max_value and
                     rec.insurance_salary > config.max_value):
                raise ValidationError(
                    _('Insurance salary must be between '
                      '%(min_value)s - %(max_value)s') % {
                          "min_value": config.min_value,
                          "max_value": config.max_value
                      }
                )

    @api.depends('date_from', 'date_to')
    def _compute_duration(self):
        """ Compute duration value """
        for rec in self:
            date_from = rec.date_from or fields.date.today()
            date_to = rec.date_to or fields.date.today()
            date_to = date_to + relativedelta(days=1)
            date_difference = relativedelta(date_to, date_from)
            rec.insurance_days = (date_to - date_from).days
            rec.duration_days = date_difference.days
            rec.duration_months = date_difference.months
            rec.duration_years = date_difference.years

    @api.constrains('date_from', 'date_to')
    def _check_date(self):
        """ Validate date """
        for record in self:
            start = record.date_from
            end = record.date_to
            overlaps = self.env['employee.insurance.history'].search([
                ('id', '!=', record.id),
                ('employee_id', '=', record.employee_id.id), '|', '&',
                ('date_from', '<=', start), ('date_to', '>=', start), '&',
                ('date_from', '<=', end), ('date_to', '>=', end),
            ])
            if overlaps or self.env['employee.insurance.history']. \
                    search_count([('employee_id', '=', record.employee_id.id),
                                  ('date_to', '=', False)]) > 1:
                raise ValidationError(_("Insurance period is overlapped"))
