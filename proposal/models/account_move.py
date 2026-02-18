""" Initialize Account Move """

from odoo import fields, models


class AccountMove(models.Model):
    """
        Inherit Account Move:
         - 
    """
    _inherit = 'account.move'

    proposal_id = fields.Many2one(
        'proposal.proposal'
    )
    analytic_account_id = fields.Many2one(
        related='proposal_id.analytic_account_id',
        readonly=False,
        store=True
    )
    claim_id = fields.Many2one(
        'proposal.claim'
    )
    vendor_claim_id = fields.Many2one(
        'proposal.vendor.claim'
    )

class AccountMoveLine(models.Model):
    """
        Inherit Account Move Line:
         - 
    """
    _inherit = 'account.move.line'

    price_unit = fields.Float(
        string='Unit Price',
        compute="_compute_price_unit", store=True, readonly=False, precompute=True,
        digits=(16, 5)
    )