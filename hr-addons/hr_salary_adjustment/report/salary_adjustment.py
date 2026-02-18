""" Salary Adjustment """
from odoo import api, models


# pylint: disable=unused-argument
class HrSalaryAdjustment(models.AbstractModel):
    """ salary adjustment report """
    _name = 'report.hr_salary_adjustment.salary_adjustment_template'
    _description = 'Salary Adjustment Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        """ prepare values to be printed """
        docs = []
        total_payslips = self.env['hr.payslip']
        for doc in data['docs']:
            employee = self.env['hr.employee'].browse(doc['employee_id'])
            payslips = self.env['hr.payslip'].browse(doc['payslip_ids'])
            docs.append({
                'employee_id': employee,
                'payslips': payslips
            })
            total_payslips += payslips
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': docs,
            'codes': data['codes'],
            'total_payslips': total_payslips,
        }
