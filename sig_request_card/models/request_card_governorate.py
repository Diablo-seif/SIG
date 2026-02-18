from odoo import fields, models


class RequestCardGovernorate(models.Model):
    _name = 'request.card.governorate'

    name = fields.Char(required=True)
