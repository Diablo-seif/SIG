""" Res Company """

from odoo import fields, models


class ResCompany(models.Model):
    """ inherit Res Company to add payroll configuration"""
    _inherit = 'res.company'

    month_start = fields.Selection(
        [('date_from', 'Date From'),
         ('date_to', 'Date To')],
        default='date_from',
        required=True
    )
