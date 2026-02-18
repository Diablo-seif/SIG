""" HR Employee """
from odoo import fields, models


class HrEmployee(models.AbstractModel):
    """ inherit HR Employee"""
    _inherit = 'hr.employee'

    eg_insurance_amount = fields.Float(
        related='contract_id.eg_insurance_amount',
        string='Insurance Amount',
        store=True
    )