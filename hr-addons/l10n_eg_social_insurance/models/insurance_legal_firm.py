""" Insurance Legal Firm """

from odoo import fields, models


class InsuranceLegalFIrm(models.Model):
    """ Insurance Legal Firm  """
    _name = "insurance.legal.firm"
    _description = 'Insurance Legal Firm'
    _sql_constraints = [
        ('unique_name', 'UNIQUE(name)', 'Name must be unique')
    ]

    name = fields.Char(
        required=True,
        translate=True
    )
