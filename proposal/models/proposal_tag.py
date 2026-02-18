""" Initialize Proposal Tag """

from random import randint

from odoo import fields, models


class ProposalTag(models.Model):
    """
        Initialize Proposal Tag:
         - 
    """
    _name = 'proposal.tag'
    _description = 'Proposal Tag'
    _check_company_auto = True

    name = fields.Char(
        required=True,
        translate=True,
    )
    active = fields.Boolean(
        default=True
    )
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
    )
    color = fields.Integer(
        default=randint(1, 11)
    )
    is_outsourcing = fields.Boolean()
    
