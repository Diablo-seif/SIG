""" Inherit deduction Tax report to add action create bill """

from odoo import _, models


class DeductionLineReport(models.Model):
    """
    Inherit deduction Tax report to add action create bill
    """
    _inherit = "deduction.line.report"

    def action_create_settlement(self):
        """ action create settlement """
        return {'name': _('Settlement Deduction Tax'),
                'view_mode': 'form', 'type': 'ir.actions.act_window',
                'res_model': 'settlement.deduction.tax.wizard',
                'context': self.env.context, 'target': 'new'}
