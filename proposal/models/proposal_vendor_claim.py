""" Initialize Proposal Vendor Claim """

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProposalVendorClaim(models.Model):
    """
        Initialize Proposal Vendor Claim:
         -
    """
    _name = 'proposal.vendor.claim'
    _description = 'Proposal Vendor Claim'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _check_company_auto = True

    state = fields.Selection(
        [('draft', 'Draft'),
         ('propose', 'Propose'),
         ('done', 'Done')],
        default='draft',
        string='Status'
    )
    name = fields.Char(
        default=_("New"),
        copy=False
    )
    active = fields.Boolean(
        default=True
    )
    claim_id = fields.Many2one(
        'proposal.claim',
        required=True
    )
    proposal_id = fields.Many2one(
        'proposal.proposal',
        related='claim_id.proposal_id',
        store=True
    )
    partner_id = fields.Many2one(
        'res.partner',
        required=True
    )
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        related='proposal_id.analytic_account_id',
        store=True
    )
    claim_date = fields.Date(
        default=fields.Date.today()
    )
    line_ids = fields.One2many(
        'proposal.vendor.claim.line',
        'vendor_claim_id'
    )
    move_ids = fields.One2many(
        'account.move',
        'vendor_claim_id'
    )

    def action_create_bill(self):
        """ Action Create Bill """
        for rec in self:
            move = self.env['account.move'].sudo().create({
                'move_type': 'in_invoice',
                'partner_id': rec.partner_id.id,
                'invoice_date': fields.Date.today(),
                'proposal_id': rec.proposal_id.id,
                'vendor_claim_id': rec.id,
                'invoice_line_ids': [(0, 0, {
                    'product_id': line.product_id.id,
                    'name': line.name,
                    'quantity': line.current_qty,
                    'price_unit': line.unit_cost,
                    'tax_ids': line.tax_ids.ids,
                    'analytic_distribution': {
                        rec.proposal_id.analytic_account_id.id: 100
                    },
                }) for line in rec.line_ids]
            })
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'account.move',
                'name': _('Account Move'),
                'view_mode': 'form',
                'res_id': move.id,
            }

    def action_view_bills(self):
        """ :return Account Move action """
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'name': _('Bills'),
            'view_mode': 'list,form',
            'domain': [('vendor_claim_id', '=', self.id)],
            'views': [(False, 'list'), (False, 'form')],
        }

    def action_propose(self):
        """ Action Propose """
        for rec in self:
            rec.state = 'propose'

    def action_done(self):
        """ Action Done """
        for rec in self:
            rec.state = 'done'

    @api.onchange('proposal_id')
    def _onchange_proposal_id(self):
        """ proposal_id """

        self.line_ids = [(5,)] + [(0, 0, {
            'claim_line_id': line.id,
            'product_id': line.product_id.id,
            'name': line.name,
            'uom_id': line.uom_id.id,
            'original_qty': line.current_qty,
            'previous_qty': sum(
                line.vendor_claim_line_ids.mapped('current_qty')),
        }) for line in self.claim_id.line_ids]

    @api.model
    def create(self, vals_list):
        """
            Override create method
             - sequence name
        """
        res = super().create(vals_list)
        if res.name == _('New'):
            res.name = res.claim_id.name + res.claim_id.vendor_claim_sequence_id._next()
        return res


class ProposalVendorClaimLine(models.Model):
    """
        Initialize Proposal Vendor Claim Line:
         -
    """
    _name = 'proposal.vendor.claim.line'
    _description = 'Proposal Vendor Claim Line'
    _check_company_auto = True

    name = fields.Char(
        required=True,
        string="Description"
    )
    sequence = fields.Integer(string="Sequence", default=10)
    product_id = fields.Many2one(
        'product.product',
        required=True
    )
    uom_id = fields.Many2one(
        'uom.uom',
        string='Unit Of Measure',
        required=True
    )
    current_qty_percentage = fields.Float()
    current_qty = fields.Float(
        compute='_compute_current_qty',
        inverse='_inverse_current_qty',
        store=True
    )
    current_amount = fields.Float(
        compute='_compute_current_amount',
        store=True
    )
    original_qty = fields.Float()
    previous_qty = fields.Float()
    cumulative_qty = fields.Float(
        compute='_compute_cumulative_qty',
        store=True
    )
    cumulative_percentage = fields.Float(
        compute='_compute_cumulative_qty',
        store=True
    )
    remaining_qty = fields.Float(
        compute='_compute_remaining_qty',
        store=True
    )
    vendor_claim_id = fields.Many2one(
        'proposal.vendor.claim'
    )
    claim_line_id = fields.Many2one(
        'proposal.claim.line'
    )
    proposal_line_id = fields.Many2one(
        'proposal.line',
        related='claim_line_id.proposal_line_id',
        store=True
    )
    tax_ids = fields.Many2many(
        'account.tax',
        'vendor_claim_purchase_tax_rel',
        'vendor_claim_id',
        'tax_id',
        related='proposal_line_id.purchase_tax_ids',
        store=True
    )
    unit_cost = fields.Float(
        related='proposal_line_id.unit_cost',
        store=True
    )
    currency_id = fields.Many2one(
        related='proposal_line_id.currency_id',
        store=True
    )

    @api.depends('previous_qty', 'original_qty')
    def _compute_remaining_qty(self):
        """ Compute remaining_qty value """
        for rec in self:
            rec.remaining_qty = rec.original_qty - rec.previous_qty

    @api.depends('previous_qty', 'current_qty')
    def _compute_cumulative_qty(self):
        """ Compute cumulative_qty value """
        for rec in self:
            cumulative_qty = rec.current_qty + rec.previous_qty
            rec.cumulative_qty = cumulative_qty
            rec.cumulative_percentage = rec.original_qty and cumulative_qty / rec.original_qty or 0

    @api.constrains('cumulative_percentage')
    def _check_cumulative_percentage(self):
        """ Validate cumulative_percentage """
        for rec in self:
            if rec.cumulative_percentage > 1:
                raise ValidationError(_('Cannot Exceed original qty'))

    @api.depends('original_qty', 'current_qty_percentage')
    def _compute_current_qty(self):
        """Compute Current Qty"""
        for rec in self:
            current_qty = rec.original_qty * rec.current_qty_percentage
            rec.current_qty = current_qty

    @api.depends('current_qty', 'unit_cost')
    def _compute_current_amount(self):
        """Compute Current Amount"""
        for rec in self:
            rec.current_amount = rec.current_qty * rec.unit_cost

    @api.onchange('original_qty', 'current_qty')
    def _inverse_current_qty(self):
        """Inverse Current Qty"""
        for rec in self:
            rec.current_qty_percentage = rec.original_qty and rec.current_qty / rec.original_qty or 0
