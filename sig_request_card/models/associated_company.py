from odoo import fields, models


class AssociatedCompany(models.Model):
    _name = 'associated.company'
    _description = 'Associated Companies'

    name = fields.Char()
