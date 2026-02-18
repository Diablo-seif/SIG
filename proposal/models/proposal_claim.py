""" Initialize Proposal Claim """

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProposalClaim(models.Model):
    """
        Initialize Proposal Claim:
         -
    """
    _name = 'proposal.claim'
    _description = 'Proposal Claim'
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
        # default=_("New"),
        default=lambda self:_("New"),

    copy=False
    )
    active = fields.Boolean(
        default=True
    )
    proposal_id = fields.Many2one(
        'proposal.proposal',
        required=True
    )
    partner_id = fields.Many2one(
        'res.partner',
        related='proposal_id.partner_id',
        store=True
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
        'proposal.claim.line',
        'claim_id'
    )
    vendor_claim_sequence_id = fields.Many2one(
        'ir.sequence',
    )
    vendor_claim_ids = fields.One2many(
        'proposal.vendor.claim',
        'claim_id'
    )

    move_ids = fields.One2many(
        'account.move',
        'vendor_claim_id'
    )

    def action_create_invoice(self):
        """ Action Create Bill """
        for rec in self:
            # so_invoice = self.env['sale.advance.payment.inv'].create({
            #     'sale_order_ids': self.proposal_id.sale_ids.ids,
            #     'advance_payment_method': 'delivered',
            # })
            # create_invoices

            move = self.env['account.move'].sudo().create({
                'move_type': 'out_invoice',
                'partner_id': rec.partner_id.id,
                'invoice_date': fields.Date.today(),
                'proposal_id': rec.proposal_id.id,
                'claim_id': rec.id,
                'invoice_line_ids': [(0, 0, {
                    'product_id': line.product_id.id,
                    'name': line.name,
                    'quantity': line.current_qty,
                    'price_unit': line.unit_price,
                    'tax_ids': line.tax_ids.ids,
                    'sale_line_ids':
                        rec.proposal_id.sale_ids.order_line.filtered(
                            lambda r: r.name == line.name and
                                      r.product_id == line.product_id).ids,
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

    def action_view_invoices(self):
        """ :return Account Move action """
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'name': _('Invoices'),
            'view_mode': 'list,form',
            'domain': [('claim_id', '=', self.id)],
            'views': [(False, 'list'), (False, 'form')],
        }

    def action_vendor_claim(self):
        """ :return  action """
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'create.vendor.claim',
            'name': _('Vendor Claim'),
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_claim_id': self.id,
                'default_claim_wizard_line_ids': [(0, 0, {
                    'proposal_claim_line_id': line.id,
                    'available_qty': line.current_qty - line.vendor_claimed_qty,
                }) for line in self.line_ids if
                                                  line.current_qty - line.vendor_claimed_qty > 0]
            },
        }

    def action_view_vendor_claim(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'proposal.vendor.claim',
            'name': _('Vendor Claims'),
            'view_mode': 'list,form',
            'domain': [('claim_id', '=', self.id)],
        }

    def _create_claim_sequence(self):
        """  Create Sequence """
        for rec in self:
            if not rec.vendor_claim_sequence_id:
                rec.vendor_claim_sequence_id = self.env['ir.sequence'].sudo().create({
                    'name': f"vendor {rec.name} claim",
                    'code': f"vendor.{rec.name}.claim",
                    'prefix': '/VEN/',
                    'padding': 2,
                    'number_next': 1,
                    'number_increment': 1,
                    'company_id': False,
                })

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
            'proposal_line_id': line.id,
            'product_id': line.product_id.id,
            'name': line.name,
            'uom_id': line.uom_id.id,
            'original_qty': line.product_uom_qty,
            'previous_qty': sum(line.claim_line_ids.mapped('current_qty')),
        }) for line in self.proposal_id.line_ids.filtered(lambda r: r.display_type == False)]

    @api.model
    def create(self, vals_list):
        """
            Override create method
             - sequence name
        """
        res = super().create(vals_list)
        if res.name == _('New'):
            res.name = res.proposal_id.name + res.proposal_id.claim_sequence_id._next()
        res._create_claim_sequence()
        return res


class ProposalClaimLine(models.Model):
    """
        Initialize Proposal Claim Line:
         -
    """
    _name = 'proposal.claim.line'
    _description = 'Proposal Claim Line'
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
    claim_id = fields.Many2one(
        'proposal.claim',
        ondelete='cascade'
    )
    proposal_line_id = fields.Many2one(
        'proposal.line'
    )
    unit_price = fields.Float(
        related='proposal_line_id.unit_price',
        store=True
    )
    currency_id = fields.Many2one(
        related='proposal_line_id.currency_id',
        store=True
    )
    tax_ids = fields.Many2many(
        'account.tax',
        'claim_sale_tax_rel',
        'claim_id',
        'tax_id',
        related='proposal_line_id.sales_tax_ids',
        store=True
    )
    vendor_claim_line_ids = fields.One2many(
        'proposal.vendor.claim.line',
        'claim_line_id'
    )
    vendor_claimed_qty = fields.Float(
        compute='_compute_vendor_claimed_qty',
        store=True
    )

    @api.depends('vendor_claim_line_ids.current_qty')
    def _compute_vendor_claimed_qty(self):
        """ Compute vendor_claimed_qty value """
        for rec in self:
            rec.vendor_claimed_qty = sum(
                rec.vendor_claim_line_ids.mapped('current_qty'))

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

    @api.depends('current_qty', 'unit_price')
    def _compute_current_amount(self):
        """Compute Current Amount"""
        for rec in self:
            rec.current_amount = rec.current_qty * rec.unit_price

    @api.onchange('original_qty', 'current_qty')
    def _inverse_current_qty(self):
        """Inverse Current Qty"""
        for rec in self:
            rec.current_qty_percentage = rec.original_qty and rec.current_qty / rec.original_qty or 0
