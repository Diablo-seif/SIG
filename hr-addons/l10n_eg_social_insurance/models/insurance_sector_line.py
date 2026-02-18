""" Initialize Insurance Sector Line """

from odoo import fields, models


class InsuranceSectorLine(models.Model):
    """ insurance Sectors Line """
    _name = "insurance.sector.line"
    _description = 'Insurance Sector Details'

    _sql_constraints = [
        ('unique_name',
         'UNIQUE(name,sector_id)',
         'Name must be unique per sector')
    ]
    name = fields.Char(
        required=True,
        translate=True
    )
    employee_percentage = fields.Float()
    company_percentage = fields.Float()
    sector_id = fields.Many2one(
        'insurance.sector'
    )
