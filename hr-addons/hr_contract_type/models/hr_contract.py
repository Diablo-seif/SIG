""" Initialize Hr Contract """

from odoo import fields, models


class HrContract(models.Model):
    """
        Inherit Hr Contract:
    """
    _inherit = 'hr.contract'

    contract_type = fields.Selection(
        [('PFI', 'PFI'),
         ('CDI', 'CDI'),
         ('CDD', 'CDD')]
    )
