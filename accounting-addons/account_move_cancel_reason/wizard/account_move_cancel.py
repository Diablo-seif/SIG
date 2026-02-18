""" Initialize account.move.cancel"""
from odoo import fields, models


class AccountMoveCancel(models.TransientModel):
    """ wizard to choose cancel reason"""
    _name = "account.move.cancel"
    _description = "Add Invoice Reason"

    cancel_reason_id = fields.Many2one("account.move.cancel.reason",
                                       string="Cancellation Reason",
                                       required=True)

    def action_cancel(self):
        """ allow to cancel journal entry and update cancel reason """
        if self.env.context.get('active_model') == 'account.move':
            active_id = self.env.context.get('active_id')
            invoice_obj = self.env['account.move'].browse(active_id)
            invoice_obj.write(
                {'cancel_reason_id': self.cancel_reason_id.id})
            invoice_obj.with_context(appear_wizard=False).button_cancel()
