""" Initialize account.move.cancel.reason """
from odoo import fields, models


class AccountMoveCancelReason(models.Model):
    """ store cancel reasons """
    _name = "account.move.cancel.reason"
    _description = "Journal Entry Cancel Reason"

    name = fields.Char(string='Cancel Reason')
    active = fields.Boolean(default=True)
