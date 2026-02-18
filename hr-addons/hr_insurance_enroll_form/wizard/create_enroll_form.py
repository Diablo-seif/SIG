""" Create Enroll Form """

from odoo import fields, models


# pylint: disable=protected-access
class CreateEnrollForm(models.TransientModel):
    """ Create Enroll Form """
    _name = 'create.enroll.form'
    _description = 'Create Enroll Form'

    method = fields.Selection(
        [('percentage', 'Percentage'),
         ('fixed', 'Fixed')],
        default='percentage'
    )
    amount = fields.Float(string="Value")
    round_value = fields.Float()
    date = fields.Date(
        default=fields.Date.today()
    )

    def create_enroll_form(self):
        """ Create Enroll Form """
        self.ensure_one()
        active_ids = self.env.context.get('active_ids')
        employees = self.env['hr.employee'].browse(active_ids).filtered(
            lambda r: r.insured and r.contract_id.state == 'open'
        )
        enroll_form = self.env['hr.insurance.enroll.form'].create({
            'company_id': self.env.company.id,
            'form_date': self.date,
            'form_line_ids':
                [(0, 0, {
                    'employee_id': emp.id,
                    'employee_insurance_number':
                        int(emp.employee_insurance_number),
                    'identification_id': emp.identification_id,
                    'insurance_date': emp.insurance_date,
                    'insured_salary': emp.get_insurance_salary(
                        self.method, self.amount, self.round_value, self.date),
                    'gross_salary': emp.gross_salary,
                    'currency_id': emp.currency_id.id,
                }) for emp in employees]
        })
        enroll_form._onchange_company_id()
