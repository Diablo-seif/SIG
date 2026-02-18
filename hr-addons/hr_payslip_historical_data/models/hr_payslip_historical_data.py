""" Hr Payslip Historical Data """

from odoo import fields, models


class HrPayslipHistoricalData(models.Model):
    """ Historical Data Model """

    _name = 'hr.payslip.historical.data'
    _description = 'Payslip Historical Data'

    def name_get(self):
        """
        Returns a textual representation for the records.
        """
        result = []
        for rec in self:
            result.append((rec.id, "%s In %s/%s" % (
                rec.employee_id.name, rec.month, rec.year)))
        return result

    employee_id = fields.Many2one('hr.employee', required=True)
    salary_rule_id = fields.Many2one('hr.salary.rule')
    salary_rule_category_id = fields.Many2one('hr.salary.rule.category')
    payslip_id = fields.Many2one('hr.payslip')
    month = fields.Integer(required=True)
    year = fields.Integer(required=True)
    value = fields.Float(required=True)
