""" HR Contract Type """

from odoo import fields, models


class HrContractType(models.Model):
    """ HR Contract Type """
    _name = 'hr.contract.type'
    _description = 'Contract Type'

    name = fields.Char(required=True)
    sequence = fields.Integer()
