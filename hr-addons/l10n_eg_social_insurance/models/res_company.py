""" Company l10n """

from odoo import fields, models


class ResCompany(models.Model):
    """ Insurance Company Information """
    _inherit = 'res.company'

    insurance_name = fields.Char(
        translate=True
    )
    legal_firm_id = fields.Many2one(
        'insurance.legal.firm'
    )
    company_number = fields.Char()
    company_insurance_number = fields.Char(
        string='Insurance Number'
    )
    start_date = fields.Date()
    insurance_owner = fields.Char(
        translate=True
    )
    insurance_owner_position = fields.Char(
        translate=True
    )
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
    building_number = fields.Char()
    insurance_street = fields.Char()
    insurance_street2 = fields.Char()
    insurance_zip = fields.Char()
    insurance_city = fields.Char()
    insurance_state = fields.Char()
    insurance_country = fields.Char()
    area = fields.Char()
