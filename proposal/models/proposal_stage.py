""" Initialize Proposal Stage """

from odoo import fields, models


class ProposalStage(models.Model):
    """
        Initialize Proposal Stage:
         - 
    """
    _name = 'proposal.stage'
    _description = 'Proposal Stage'
    _check_company_auto = True

    _sql_constraints = [
        ('state_uniq', 'unique(state)', 'The value of state must be unique!')
    ]

    name = fields.Char(
        required=True,
        translate=True,
    )
    sequence = fields.Integer(
        default=10
    )
    active = fields.Boolean(
        default=True
    )
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
    )
    is_done = fields.Boolean()
    is_lost = fields.Boolean()
    # state = fields.Selection(
    #     [('draft', 'Draft'),
    #      ('sent_to_purchase', 'Sent To Purchase'),
    #      ('sent_to_sales', 'Sent To Sales'),
    #      ('done', 'Won'),
    #      ('lost', 'Lost')],
    #     string='Status'
    # )
    is_sent_to_purchase = fields.Boolean()
    is_sent_to_sales = fields.Boolean()
    is_draft = fields.Boolean()
    is_cancelled = fields.Boolean()
    