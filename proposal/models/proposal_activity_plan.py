""" Initialize Proposal Activity Plan """

from odoo import fields, models


class ProposalActivityPlan(models.Model):
    """
        Initialize Proposal Activity Plan:
         -
    """
    _name = 'proposal.activity.plan'
    _description = 'Proposal Activity Plan'

    active = fields.Boolean(
        default=True,
    )
    activity_type_id = fields.Many2one(
        'mail.activity.type',
        required=True
    )
    description = fields.Char()
    user_ids = fields.Many2many(
        'res.users',
        required=True
    )
    planned_after = fields.Integer()
    proposal_state = fields.Selection(
        [('draft', 'Draft'),
         ('sent_to_purchase', 'Sent To Purchase'),
         ('sent_to_sales', 'Sent To Sales')],
        string='Proposal State',
        required=True
    )
