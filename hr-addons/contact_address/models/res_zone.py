""" Initialize Res Zone """

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError, Warning


class ResCountryZone(models.Model):
    """
        Initialize Res Country Zone:
         -
    """
    _name = 'res.country.zone'
    _description = 'Country Zone'
    _check_company_auto = True

    name = fields.Char(
        required=True,
        translate=True,
    )
    code = fields.Char(
        required=True,
    )
    state_id = fields.Many2one(
        'res.country.state', required=True,
        domain="[('country_id', '=?', country_id)]"
    )
    country_id = fields.Many2one(
        'res.country', required=True,
    )

    @api.onchange('state_id')
    def _onchange_state_id(self):
        """ state_id """
        if self.state_id:
            self.country_id = self.state_id.country_id.id
