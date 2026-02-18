""" Initialize Create Rfq """

from odoo import fields, models


class CreateRfq(models.TransientModel):
    """
        Initialize Create Rfq:
         -
    """
    _name = 'create.rfq'
    _description = 'Create RFQ'

    partner_ids = fields.Many2many(
        'res.partner'
    )
    proposal_id = fields.Many2one(
        'proposal.proposal',
        default=lambda self: self.env.context.get('active_id')
    )

    def action_create_rfq(self):
        """ Action Create Rfq """
        for partner in self.partner_ids:
            self.env['purchase.order'].create({
                'proposal_id': self.proposal_id.id,
                'partner_id': partner.id,
                'date_order': self.proposal_id.date_order,
                'analytic_account_id': self.proposal_id.analytic_account_id.id,
                'order_line': [(0, 0, {
                    'product_id': line.product_id.id,
                    'name': line.name,
                    'analytic_distribution': {self.proposal_id.analytic_account_id.id: 100},
                    'product_uom': line.uom_id.id,
                    'product_qty': line.product_uom_qty,
                    'taxes_id': line.purchase_tax_ids.ids,
                }) for line in self.proposal_id.line_ids],

            })
