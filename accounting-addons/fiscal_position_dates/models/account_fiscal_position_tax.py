""" init object account.fiscal.position.tax """

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountFiscalPositionTax(models.Model):
    """ init object account.fiscal.position.tax """
    _inherit = 'account.fiscal.position.tax'

    @api.constrains('date_from', 'date_to')
    def _constrains_dates(self):
        """
        Constrains_dates
        """
        for rec in self:
            if rec.date_from and rec.date_to and rec.date_from > rec.date_to:
                raise UserError(_("'Date From' must be earlier 'Date To'."))

    date_from = fields.Date()
    date_to = fields.Date()
