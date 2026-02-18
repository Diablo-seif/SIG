""" inherit account.move """
from odoo import _, fields, models


# pylint: disable=no-member
class AccountMove(models.Model):
    """ allow to cancel with reason """
    _inherit = "account.move"

    cancel_reason_id = fields.Many2one("account.move.cancel.reason",
                                       string="Cancellation Reason",
                                       tracking=True)

    def button_cancel(self):
        """ inherit to appear wizard instead of cancel """
        if self.env.context.get('appear_wizard', False):
            return {
                'name': _('Add Cancel Reason'),
                'view_mode': 'form',
                'res_model': 'account.move.cancel',
                'type': 'ir.actions.act_window',
                'target': 'new'}
        return super(AccountMove, self).button_cancel()

    def button_draft(self):
        """ inherit to set cancel reason empty """
        res = super(AccountMove, self).button_draft()
        self.write({"cancel_reason_id": False})
        return res
