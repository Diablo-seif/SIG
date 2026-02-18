
from odoo import models, fields

class EmployeeType(models.Model):
    
    _name = 'employee.type'
    _description = 'Employee Type'
    
    name = fields.Char(required=True)
    type = fields.Selection([
        ('external', 'External'),
        ('internal', 'Internal'), 
    ], required=True)    
    state_id = fields.Many2one('res.country.state')
    partner_id = fields.Many2one('res.partner')
    company_id = fields.Many2one('res.company')
    
    