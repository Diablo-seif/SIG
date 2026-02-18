""" Insurance Sector """

from odoo import api, fields, models


class InsuranceSector(models.Model):
    """ insurance Sectors """
    _name = "insurance.sector"
    _description = 'Insurance Sector'
    _sql_constraints = [
        ('unique_name', 'UNIQUE(name)', 'Name must be unique')
    ]
    name = fields.Char(
        required=True,
        translate=True
    )
    employee_percentage = fields.Float(
        compute='_compute_percentage',
        store=True
    )
    company_percentage = fields.Float(
        compute='_compute_percentage',
        store=True
    )
    sector_period_ids = fields.One2many(
        'insurance.sector.period',
        'sector_id',
        string='Period Details'
    )

    @api.depends('sector_period_ids.employee_percentage',
                 'sector_period_ids.company_percentage')
    def _compute_percentage(self):
        """ Compute percentage value """
        for rec in self:
            employee_percentage = 0
            company_percentage = 0
            for period in rec.sector_period_ids:
                employee_percentage = period.employee_percentage
                company_percentage = period.company_percentage
            rec.employee_percentage = employee_percentage
            rec.company_percentage = company_percentage
