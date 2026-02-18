"""init model """

from odoo import models, fields, _
from odoo.exceptions import UserError


class VatcloseReport(models.TransientModel):
    """
    Close VAT Tax report for month
    """
    _name = "vat.close.report"
    _description = "VAT Close Report"

    mark_as_reported = fields.Boolean()
    close_year = fields.Integer()
    close_month = fields.Selection([('1', '1'),
                                    ('2', '2'),
                                    ('3', '3'),
                                    ('4', '4'),
                                    ('5', '5'),
                                    ('6', '6'),
                                    ('7', '7'),
                                    ('8', '8'),
                                    ('9', '9'),
                                    ('10', '10'),
                                    ('11', '11'),
                                    ('12', '12')])

    def action_close_report(self):
        """  call close report action """
        if self.close_month:
            self.env['account.move'].action_close_report(self.close_month,
                                                         self.mark_as_reported,
                                                         self.close_year)
            model_name = self.env.context.get('report_model')
            if model_name == 'vat.sales.report.grouped' and \
                    self.mark_as_reported:
                self.env[model_name].copy_to_monthly(self.close_month,
                                                     self.close_year)
        else:
            raise UserError(_('Please select a month.'))
