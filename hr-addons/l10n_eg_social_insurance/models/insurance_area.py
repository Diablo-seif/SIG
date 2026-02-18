""" Insurance Area """

from odoo import fields, models


class ResCountryStateArea(models.Model):
    """ Res Country State Area """
    _name = 'res.country.state.area'
    _description = 'Res Country State Area'

    name = fields.Char(
        translate=True
    )
    country_id = fields.Many2one(
        related='state_id.country_id',
        store=True
    )
    state_id = fields.Many2one(
        'res.country.state'
    )
