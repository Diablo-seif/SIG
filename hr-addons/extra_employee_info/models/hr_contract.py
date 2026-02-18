""" Inherit hr.contract """

from odoo import fields, models

class HrContract(models.Model):
    _inherit = 'hr.contract'
    
    net_salary_monthly = fields.Monetary()
    net_salary_daily = fields.Monetary()
    