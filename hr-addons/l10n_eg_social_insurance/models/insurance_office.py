""" Insurance Office """

from odoo import api, fields, models


class InsuranceOffice(models.Model):
    """ Insurance Office  """
    _name = "insurance.office"
    _description = 'Insurance Office'
    _sql_constraints = [
        ('unique_name', 'UNIQUE(name)', 'Name must be unique')
    ]

    name = fields.Char(
        required=True,
        translate=True
    )
    state_id = fields.Many2one(
        'res.country.state',
        required=True,
        domain=lambda self: [('country_id', '=',
                              self.env.company.country_id.id)]
    )
    area_id = fields.Many2one(
        'res.country.state.area',
        domain="[('state_id', '=', state_id)]",
        required=True
    )

    @api.onchange('state_id')
    def _onchange_state_id(self):
        """ Clear area when changing state """
        self.area_id = False
