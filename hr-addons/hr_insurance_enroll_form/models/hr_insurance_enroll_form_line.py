""" Initialize Hr Insurance Enroll Form Line """

from odoo import api, fields, models


class HrInsuranceEnrollFormLine(models.Model):
    """ HR Enroll Form Line """
    _name = 'hr.insurance.enroll.form.line'
    _description = 'Insurance Enroll Form Line'
    _order = 'employee_insurance_number'

    employee_id = fields.Many2one(
        'hr.employee',
        domain="[('insured', '=', True)]",
        required=True
    )
    employee_insurance_number = fields.Integer(string="Insurance Number")
    identification_id = fields.Char()
    insurance_date = fields.Date()
    insured_salary = fields.Monetary()
    gross_salary = fields.Monetary()
    basic_salary = fields.Monetary()
    variable_salary = fields.Monetary()
    currency_id = fields.Many2one('res.currency')
    form_id = fields.Many2one('hr.insurance.enroll.form')

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        """ employee_id """
        self.employee_insurance_number = \
            int(self.employee_id.employee_insurance_number)
        self.identification_id = self.employee_id.identification_id
        self.insurance_date = self.employee_id.insurance_date
        self.insured_salary = self.employee_id.insured_salary
        self.gross_salary = self.employee_id.gross_salary
        self.currency_id = self.employee_id.currency_id
