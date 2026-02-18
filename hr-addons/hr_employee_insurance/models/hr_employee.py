""" HR Employee """
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HrEmployee(models.AbstractModel):
    """ inherit HR Employee Base to add insurance fields"""
    _inherit = 'hr.employee.base'

    insurance_date = fields.Date()
    employee_insurance_number = fields.Integer(
        string="Insurance Number"
    )
    name_in_arabic = fields.Char()
    insurance_sector_ids = fields.Many2many(
        'insurance.sector',
        related='company_id.insurance_sector_ids'
    )
    insurance_sector_id = fields.Many2one(
        'insurance.sector'
    )
    insured_salary = fields.Monetary()
    gross_salary = fields.Monetary()
    insurance_employee_share = fields.Float(
        compute='_compute_insurance_share',
        store=True
    )
    insurance_company_share = fields.Float(
        compute='_compute_insurance_share',
        store=True
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='company_id.currency_id',
        store=True,
    )
    insurance_office_id = fields.Many2one(
        'insurance.office'
    )
    company_number = fields.Char(
        related='company_id.company_number'
    )
    received_date = fields.Date(
        string='Received Date (1)'
    )
    received_number = fields.Char(
        string='Received Number (1)'
    )
    resignation_received_date = fields.Date(
        string='Received Date (6)'
    )
    resignation_received_number = fields.Char(
        string='Received Number (6)'
    )
    insurance_job_id = fields.Many2one(
        'insurance.job'
    )
    insurance_history_ids = fields.One2many(
        'employee.insurance.history',
        'employee_id'
    )
    owner = fields.Boolean()
    insured = fields.Boolean(
        default=True
    )
    medical_insured = fields.Boolean()


    @api.depends('insurance_sector_id', 'insured',
                 'insurance_sector_id.employee_percentage',
                 'insurance_sector_id.company_percentage',
                 'insured_salary')
    def _compute_insurance_share(self):
        """ Compute Compute Insurance Share value """
        for employee in self:
            sector = employee.insurance_sector_id
            salary = employee.insured_salary
            insurance_employee_share = 0
            insurance_company_share = 0
            if employee.insured and sector and salary > 0:
                insurance_employee_share = \
                    salary * (sector.employee_percentage / 100)
                insurance_company_share = \
                    salary * (sector.company_percentage / 100)
            employee.insurance_employee_share = insurance_employee_share
            employee.insurance_company_share = insurance_company_share

    @api.constrains('owner', 'company_id')
    def _check_owner(self):
        """ Validate owner """
        for employee in self:
            owners = self.search_count([
                ('owner', '=', True),
                ('company_id', '=', employee.company_id.id)
            ])
            if owners > 1:
                raise ValidationError(_('Owner must be unique'))
