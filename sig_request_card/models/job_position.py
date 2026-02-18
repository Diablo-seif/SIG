
from odoo import models, fields


class JobPosition(models.Model):
    _name = 'sig.job.position'

    name = fields.Char(required=True)
    for_organization = fields.Selection([
        ('alshar_alaqari', 'Al-Shahr Al-Aqari'),
        ('el_mesaha_el_Askareya', 'El-Mesaha El-Askareya'),
    ], required=True, default="alshar_alaqari")
    
