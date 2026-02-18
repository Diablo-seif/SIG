""" Initialize Purchase """

from odoo import fields, models


class PurchaseOrder(models.Model):
    """
        Inherit Purchase Order:
         -
    """
    _inherit = 'purchase.order'

    proposal_id = fields.Many2one(
        'proposal.proposal'
    )

    analytic_account_id = fields.Many2one(
        'account.analytic.account'
    )

    def _prepare_invoice(self):
        invoice_vals = super()._prepare_invoice()
        if self.proposal_id:
            invoice_vals.update({'proposal_id': self.proposal_id.id})
        return invoice_vals


class PurchaseOrderLine(models.Model):
    """
        Inherit Purchase Order Line:
         -
    """
    _inherit = 'purchase.order.line'

    price_unit = fields.Float(
        string='Unit Price', required=True,
        digits=(16,5),
        compute="_compute_price_unit_and_date_planned_and_name", readonly=False, store=True)