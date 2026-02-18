""" Initialize Proposal Lost Reason """

from odoo import fields, models


class ProposalLostReason(models.Model):
    """
        Initialize Proposal Lost Reason:
         -
    """
    _name = 'proposal.lost.reason'
    _description = 'Proposal Lost Reason'
    _check_company_auto = True

    name = fields.Char(
        required=True,
        translate=True,
    )
    description = fields.Text()
    active = fields.Boolean(
        default=True
    )
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
    )
