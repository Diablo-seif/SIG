""" init module res.company"""

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class ResCompany(models.Model):
    """ init module res.company"""

    _inherit = 'res.company'

    vat_warning_day = fields.Integer(
        "VAT warning Delay",
        help="# day accountant should check the VAT report",
        default=10)

    @api.constrains('vat_warning_day')
    def _constraint_vat_warning_day(self):
        for record in self:
            if not 0 < record.vat_warning_day <= 31:
                raise UserError(_("Day should between 1..31"))
