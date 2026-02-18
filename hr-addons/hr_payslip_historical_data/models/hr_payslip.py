""" update object hr.payslip """

from odoo import models


class HrPayslip(models.Model):
    """ update object hr.payslip """
    _inherit = 'hr.payslip'

    # pylint: disable=no-member
    def action_payslip_done(self):
        """
        call function super action_payslip_done
        to Add output Payslip Lines to Historical Data
        """
        res = super(HrPayslip, self).action_payslip_done()
        for record in self:
            if record.date_to and record.line_ids:
                date = record.date_to
                for rec in record.line_ids:
                    values = {
                        'employee_id': record.employee_id.id,
                        'salary_rule_id': rec.salary_rule_id.id,
                        'salary_rule_category_id': rec.category_id.id,
                        'payslip_id': record.id,
                        'month': date.month,
                        'year': date.year,
                        'value': rec.total
                    }
                    self.env['hr.payslip.historical.data'].create(values)

        return res
