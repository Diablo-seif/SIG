""" Salary Adjustment """
from odoo import _, api, fields, models
from odoo.exceptions import UserError


# pylint: disable=no-member,protected-access,no-self-use
class SalaryAdjustment(models.TransientModel):
    """ Salary Adjustment """
    _name = 'salary.adjustment'
    _description = 'Salary Adjustment'
    _inherit = 'hr.period'

    date_from = fields.Date(required=False)
    department_ids = fields.Many2many('hr.department')
    employee_ids = fields.Many2many('hr.employee')
    detailed = fields.Boolean()

    @api.constrains('date_from', 'date_to')
    def _check_date(self):
        """ overridden to stop checking overlaps """
        return True

    def print_pdf(self):
        """ print salary adjustment report """
        self.ensure_one()
        # Construct search domain
        domain = [('state', '=', 'done')]
        if self.department_ids:
            domain.append(
                ('employee_id', 'in', self.department_ids.member_ids.ids)
            )
        if self.employee_ids:
            domain.append(('employee_id', 'in', self.employee_ids.ids))
        if self.period_month_ids and (self.date_from or self.date_to):
            domain.append(
                ('payslip_month', 'in', self.period_month_ids.mapped('name'))
            )
        # Get payslips grouped by employee and salary tax
        grouped_payslip = self.env['hr.payslip'].read_group(
            domain=domain, fields=['ids:array_agg(id)'],
            groupby=['salary_tax_id', 'employee_id'], lazy=False
        )
        if not grouped_payslip:
            raise UserError(_("There is no data to print"))
        # Construct docs to be used in report
        docs = []
        payslips = self.env['hr.payslip']
        for group in grouped_payslip:
            docs.append({
                'employee_id': group['employee_id'][0],
                'payslip_ids': group['ids'],
            })
            payslips += payslips.browse(group['ids'])
        # Construct sorted unique salary rules code list
        payslip_lines = \
            payslips.line_ids if self.detailed else payslips.line_ids.filtered(
                lambda r: r.salary_rule_id.appears_on_salary_adjustment)
        codes = payslip_lines.mapped(
            lambda r: (r.salary_rule_id.code,
                       r.salary_rule_id.name,
                       r.salary_rule_id.sequence_on_salary_adjustment,
                       r.salary_rule_id.highlight_on_salary_adjustment))
        codes = sorted(self.unique_codes(codes), key=lambda tup: tup[2])
        # return report with data
        data = {
            'docs': docs,
            'codes': codes,
            'model': self.env['hr.payslip']._name,
            'ids': payslips.ids,
        }
        return self.env.ref(
            'hr_salary_adjustment.salary_adjustment_report'
        ).report_action(self, data=data)

    @staticmethod
    def unique_codes(codes):
        """ Unique Codes """
        visited = set()
        output = []
        for code, name, sequence, highlight in codes:
            if code not in visited:
                visited.add(code)
                output.append((code, name, sequence, highlight))
        return output
