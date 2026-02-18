""" HR Contract """
from odoo import fields, models


class HrContract(models.Model):
    """ inherit HR Contract """
    _inherit = 'hr.contract'

    time_off_limitation = fields.Boolean(default=True)
