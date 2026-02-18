""" inherit res.config.settings to add levelling configuration """

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    """ Inherit res.config.settings to add organization levelling config """
    _inherit = 'res.config.settings'

    organization_levelling = fields.Integer(
        related='company_id.organization_levelling',
        readonly=False,
        default=True,
        help='This Configuration to ensure that organization '
             'levels wont exceed the selected level'
    )

    @api.constrains('organization_levelling')
    def _validate_organization_levelling(self):
        """ Validate organization levelling cannot exceed 21 level """
        for config in self:
            if config.organization_levelling < 1:
                raise ValidationError(_(
                    'The organization levelling cannot be a negative number.'
                ))
