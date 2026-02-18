""" Enroll Form """

import logging

from dateutil.relativedelta import relativedelta

from odoo import api, fields
from odoo import models

LOGGER = logging.getLogger(__name__)

try:
    from num2words import num2words
except ImportError:
    LOGGER.warning("The num2words python library is not installed,"
                   " amount-to-text features won't be fully available.")
    num2words = None


# pylint: disable=too-many-instance-attributes
class HrInsuranceEnrollForm(models.Model):
    """ HR Insurance Enroll Form """
    _name = 'hr.insurance.enroll.form'
    _description = 'Insurance Enroll Form'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.model
    def _get_form_lines(self):
        """  Get Enroll Form Lines """
        employees = self.env['hr.employee'].search([
            ('insured', '=', True), ('contract_id.state', '=', 'open')
        ])
        return [(0, 0, {
            'employee_id': emp.id,
            'employee_insurance_number': int(emp.employee_insurance_number),
            'identification_id': emp.identification_id,
            'insurance_date': emp.insurance_date,
            'insured_salary': emp.insured_salary,
            'gross_salary': emp.gross_salary,
        }) for emp in employees]

    state = fields.Selection(
        [('draft', 'Draft'),
         ('confirmed', 'Confirmed'),
         ('canceled', 'Canceled')],
        default='draft',
        string='Status',
        tracking=True,
    )
    name = fields.Char(
        default='New',
        readonly=True
    )
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company.id,
        required=True
    )
    form_number = fields.Integer()
    ministerial_decree_number = fields.Integer()
    ministerial_decree_year = fields.Integer()
    insurance_name = fields.Char()
    insurance_owner = fields.Char()
    insurance_owner_position = fields.Char()
    legal_firm_id = fields.Many2one(
        'insurance.legal.firm'
    )
    company_insurance_number = fields.Char(
        string='Insurance Number'
    )
    start_date = fields.Date()
    insurance_type = fields.Selection(
        [('centralized', 'Centralized'),
         ('branch', 'Branch')]
    )
    insurance_office_id = fields.Many2one(
        'insurance.office'
    )
    insurance_sector_ids = fields.Many2many(
        'insurance.sector'
    )
    received_date = fields.Date(
        tracking=True,
    )
    received_number = fields.Char(
        tracking=True,
    )
    form_date = fields.Date(
        tracking=True,
    )
    form_line_ids = fields.One2many(
        'hr.insurance.enroll.form.line',
        'form_id',
        default=_get_form_lines
    )
    employees_count = fields.Char(
        compute='_compute_employees_count'
    )

    @api.depends('form_line_ids')
    def _compute_employees_count(self):
        """ Compute _compute_employees_count value """
        for rec in self:
            number = len(rec.form_line_ids)
            rec.employees_count = num2words(number, lang='ar').title()

    @api.model
    def create(self, vals_list):
        """ Override create method to sequence name """
        if vals_list.get('name', 'New'):
            vals_list['name'] = self.env['ir.sequence'].next_by_code(
                'enroll.form')
        return super().create(vals_list)

    @api.onchange('company_id')
    def _onchange_company_id(self):
        """ get company insurance details """
        self.insurance_name = self.company_id.insurance_name
        self.insurance_owner = self.company_id.insurance_owner
        self.insurance_owner_position = self.company_id.insurance_owner_position
        self.legal_firm_id = self.company_id.legal_firm_id.id
        self.company_insurance_number = self.company_id.company_insurance_number
        self.start_date = self.company_id.start_date
        self.insurance_type = self.company_id.insurance_type
        self.insurance_office_id = self.company_id.insurance_office_id.id
        self.insurance_sector_ids = [
            (6, 0, self.company_id.insurance_sector_ids.ids)
        ]

    def action_confirm(self):
        """ Action Confirm """
        for rec in self:
            rec.state = 'confirmed'
            for line in rec.form_line_ids:
                employee = line.employee_id
                employee.insured_salary = line.insured_salary
                vals = {
                    'date_from': rec.form_date,
                    'date_to': False,
                    'insurance_salary': line.insured_salary,
                    'variable_salary': line.variable_salary,
                    'company': self.env.company.name
                }
                history = employee.insurance_history_ids.filtered(
                    lambda r: not r.date_to)
                if history:
                    history.date_to = rec.form_date + relativedelta(days=-1)
                    history.copy(vals)
                else:
                    employee.insurance_history_ids = [(0, 0, vals)]

    def action_cancel(self):
        """ Action Cancel """
        for rec in self:
            rec.state = 'canceled'

    def action_draft(self):
        """ Action Draft """
        for rec in self:
            rec.state = 'draft'
