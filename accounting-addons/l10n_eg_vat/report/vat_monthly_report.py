"""init model """

from odoo import models, fields


class VatMonthlyReport(models.Model):
    """
    VAT Tax report monthly header
    """
    _name = "vat.monthly.report"
    _description = "VAT Tax Report Grouped Monthly"
    _order = "year desc, month desc, report_date desc"
    _rec_name = 'year'

    monthly_line_ids = fields.One2many('vat.monthly.report.line',
                                       "monthly_id", readonly=True)
    year = fields.Char(readonly=True)
    month = fields.Char(readonly=True)
    report_date = fields.Datetime(readonly=True)
    user_id = fields.Many2one("res.users", string="User")
    currency_id = fields.Many2one('res.currency', readonly=True)
    sales_total_amount = fields.Monetary(string='Sales Total', readonly=True)
    purchase_total_amount = fields.Monetary(string='Purchase Total',
                                            readonly=True)
    total_amount = fields.Monetary(string='Total', readonly=True)

    def name_get(self):
        """ override the record name """
        res = []
        for record in self:
            res.append((record.id, '%s, %s (%s)' % (record.year, record.month,
                                                    record.report_date)))
        return res
