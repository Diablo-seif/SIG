""" Initialize Create Vendor Claim """

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class CreateVendorClaim(models.TransientModel):
    """
        Initialize Create Vendor Claim:
         -
    """
    _name = 'create.vendor.claim'
    _description = 'Create Vendor Claim'

    claim_id = fields.Many2one(
        'proposal.claim'
    )
    claim_wizard_line_ids = fields.One2many(
        'create.vendor.claim.line',
        'claim_wizard_id'
    )

    def action_claim(self):
        """ Action Claim """
        partners = set(self.claim_wizard_line_ids.mapped('partner_id'))
        for partner in partners:
            line_ids = [(0, 0, {
                'product_id': line.product_id.id,
                'uom_id': line.proposal_claim_line_id.uom_id.id,
                'claim_line_id': line.proposal_claim_line_id.id,
                'proposal_line_id': line.proposal_claim_line_id.proposal_line_id.id,
                'name': line.proposal_claim_line_id.name,
                'original_qty': line.available_qty,
                'current_qty': line.qty,
            }) for line in self.claim_wizard_line_ids.filtered(
                lambda r: r.partner_id == partner and r.qty > 0)]
            if not line_ids:
                raise ValidationError(_('You must claim at least one line'))
            self.env['proposal.vendor.claim'].create({
                'partner_id': partner.id,
                'claim_id': self.claim_id.id,
                'line_ids': line_ids
            })


class CreateVendorClaimLine(models.TransientModel):
    """
        Initialize Create Vendor Claim Line:
         -
    """
    _name = 'create.vendor.claim.line'
    _description = 'Create Vendor Claim Line'

    claim_wizard_id = fields.Many2one(
        'create.vendor.claim'
    )
    partner_id = fields.Many2one(
        'res.partner',
        required=True
    )
    proposal_claim_line_id = fields.Many2one(
        'proposal.claim.line'
    )
    product_id = fields.Many2one(
        related='proposal_claim_line_id.product_id'
    )
    available_qty = fields.Float(
        digits=(15,15),
        readonly=True
    )
    qty = fields.Float(digits=(15,15))

    @api.constrains('qty')
    def _check_qty(self):
        """ Validate qty """
        for rec in self:
            if rec.qty > rec.available_qty:
                raise ValidationError(_(
                    'Cannot exceed available qty'
                ))
