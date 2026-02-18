
from odoo import fields, models

class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'
    
    type = fields.Selection([
        ('external', 'External'),
        ('internal', 'Internal'), 
    ])
    is_opened = fields.Boolean(default=True)
    start_date = fields.Date()
    end_date = fields.Date()
    