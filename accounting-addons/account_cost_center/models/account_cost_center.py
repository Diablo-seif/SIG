""" init object account.cost.center  """

from odoo import fields, models


class AccountCostCenter(models.Model):
    """ init object account.cost.center  """
    _name = 'account.cost.center'
    _description = 'Account Cost Center'

    name = fields.Char(string='Title', required=True)
    code = fields.Char(required=True)
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.company)
