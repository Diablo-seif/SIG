
from odoo import fields, models


class HrOffice(models.Model):
 
    _name = 'hr.office'
    _description = 'HR Office'

    name = fields.Char(required=True)
