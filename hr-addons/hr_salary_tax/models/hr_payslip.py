""" Initialize Hr Payslip """

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class HrPayslip(models.Model):
    """ inherit HR Payslip """
    _inherit = 'hr.payslip'

    payslip_month = fields.Char(
        compute='_compute_payslip_month',
        store=True
    )
    salary_tax_id = fields.Many2one(
        'hr.salary.tax'
    )

    @api.depends('date_from', 'date_to')
    def _compute_payslip_month(self):
        """ Compute payslip_month value """
        company = self.env.company
        for rec in self:
            if rec.date_from and rec.date_to:
                month_start = rec.date_to if \
                    company.month_start == 'date_to' else rec.date_from
                rec.payslip_month = month_start.strftime('%b %Y')

    @api.model
    def _get_year_payslip(self, employee, tax):
        """  Get current Year Payslip for specific employee"""
        year_from = fields.Date.today().replace(day=1, month=1)
        year_to = fields.Date.today().replace(day=31, month=12)
        period_months = (year_to.year - year_from.year) * 12 + \
                        (year_to.month - year_from.month)
        year_months = [
            (year_from + relativedelta(months=month)).strftime('%b %Y')
            for month in range(period_months + 1)
        ]
        return self.search([
            ('employee_id', '=', employee.id),
            ('salary_tax_id', '=', tax.id),
            ('payslip_month', 'in', year_months),
            ('state', '=', 'done')
        ])

    # pylint: disable=no-member
    def compute_sheet(self):
        """ inherit compute_sheet() """
        for payslip in self:
            tax = self.env['hr.salary.tax'].search([
                ('period_month_ids.name', '=', payslip.payslip_month)], limit=1)
            payslip.salary_tax_id = tax.id
        return super().compute_sheet()
