""" Social Insurance Config """

from odoo import fields, models


class SocialInsuranceConfig(models.Model):
    """ Social Insurance Config """
    _name = 'social.insurance.config'
    _description = 'Social Insurance Config'
    _inherit = 'hr.period'
    _sql_constraints = [(
        'max_greater_min',
        'CHECK(min_value <= max_value)',
        'Minimum value can\'t be greater than maximum value'
    )]

    method = fields.Selection(
        [('fixed', 'Fixed'),
         ('percentage', 'Percentage')],
        default='fixed'
    )
    value = fields.Float(
        required=True
    )
    min_value = fields.Float(
        'Minimum Value'
    )
    max_value = fields.Float(
        'Maximum Value'
    )
