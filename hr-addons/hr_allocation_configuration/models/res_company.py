""" Company """
from odoo import fields, models


class ResCompany(models.Model):
    """ inherit Company to add configuration """
    _inherit = 'res.company'

    time_off_years_of_insurance = fields.Integer(
        default=10, string='Years Of Insurance'
    )
    time_off_employee_age = fields.Integer(default=50, string='Employee Age')
