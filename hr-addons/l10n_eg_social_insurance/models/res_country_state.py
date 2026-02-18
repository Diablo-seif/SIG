""" Res Country State """

from odoo import fields, models


class ResCountryState(models.Model):
    """ inherit Res Country State """
    _inherit = 'res.country.state'

    area_ids = fields.One2many(
        'res.country.state.area',
        'state_id'
    )
    insurance_office_ids = fields.One2many(
        'insurance.office',
        'state_id'
    )
