""" Initialize Sale """

from odoo import _, fields, models


class SaleOrder(models.Model):
    """
        Inherit Sale Order:
         -
    """
    _inherit = 'sale.order'

    proposal_id = fields.Many2one(
        'proposal.proposal'
    )
    project_created = fields.Boolean()

    def _prepare_invoice(self):
        invoice_vals = super()._prepare_invoice()
        if self.proposal_id:
            invoice_vals.update({'proposal_id': self.proposal_id.id})
        return invoice_vals

    def action_create_project(self):
        """ Action Create Project """
        return {
            'type': 'ir.actions.act_window',
            'name': _('Create a Project'),
            'res_model': 'project.project',
            'view_mode': 'form',
            'view_id': self.env.ref(
                'project.project_project_view_form_simplified_footer').id,
            'target': 'new',
            'context': {
                'default_name': self.analytic_account_id.name,
                'default_analytic_account_id': self.analytic_account_id.id,
                'default_code': self.analytic_account_id.project_code,
                'default_proposal_id': self.proposal_id.id,
                'active_sale_id': self.id,
            }
        }


class SaleOrderLine(models.Model):
    """
        Inherit Sale Order Line:
         -
    """
    _inherit = 'sale.order.line'

    proposal_line_id = fields.Many2one(
        'proposal.line'
    )
