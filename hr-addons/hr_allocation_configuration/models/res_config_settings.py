""" inherit res.config.settings to add time off allocation configuration """
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    """ Inherit res.config.settings to add time off allocation configuration """
    _inherit = 'res.config.settings'

    time_off_years_of_insurance = fields.Integer(
        related='company_id.time_off_years_of_insurance', readonly=False,
        help='Years of insurance to change time off amount'
    )

    time_off_employee_age = fields.Integer(
        related='company_id.time_off_employee_age', readonly=False,
        help='Employee age to change time off amount'
    )
