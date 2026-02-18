""" Initialize Account Move """

from odoo import _, api, models

from odoo.tools.misc import groupby


# pylint: disable=protected-access,inconsistent-return-statements
class AccountMove(models.Model):
    """
        Inherit Account Move:
    """
    _inherit = 'account.move'

    def action_create_payment_request(self):
        """ Action Create Payment Request """
        requests = self.env['payment.request']
        invoices = self.filtered(
            lambda r: r.state == 'posted' and r.amount_residual and
            r.move_type in ['in_invoice', 'out_refund']
        )
        for currency, moves in groupby(invoices, key=lambda r: r.currency_id):
            request = requests.create({
                'currency_id': currency.id,
                'line_ids':
                    [(0, 0, self._prepare_lines(currency, partner, move)) for
                     partner, move in groupby(moves, lambda r: r.partner_id)]
            })
            requests += request
        if requests:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'payment.request',
                'name': _('Payment Requests'),
                'view_mode': 'list,form',
                'domain': [('id', 'in', requests.ids)],
            }

    @api.model
    def _prepare_lines(self, currency, partner, moves):
        """ prepare invoice """
        line = self.env['payment.request.line'].new({
            'partner_id': partner.id,
            'currency_id': currency.id,
            'move_ids': [move.id for move in moves],
            'total_payment_request':
                sum([move.amount_residual for move in moves]),
        })
        line._onchange_partner_id()
        return line._convert_to_write(line._cache)
