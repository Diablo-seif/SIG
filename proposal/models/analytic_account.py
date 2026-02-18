""" Initialize Analytic Account """

from odoo import fields, models


class AccountAnalyticAccount(models.Model):
    """
        Inherit Account Analytic Account:
         -
    """
    _inherit = 'account.analytic.account'

    project_code = fields.Char()
