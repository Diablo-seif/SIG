""" HR Salary Tax """

import math

from odoo import _, api, fields, models
from odoo.exceptions import UserError


# pylint: disable=inconsistent-return-statements,no-self-use,protected-access
# pylint: disable=too-many-locals,chained-comparison
class HrSalaryTax(models.Model):
    """ HR Salary Tax """
    _name = 'hr.salary.tax'
    _description = 'Salary Tax'
    _inherit = 'hr.period'

    active = fields.Boolean(
        default=True
    )
    name = fields.Char()
    exemption = fields.Float()
    rounding = fields.Float()
    rounding_method = fields.Selection(
        [('ceil', 'Ceiling'),
         ('floor', 'Flooring')],
        default="ceil",
        required=True
    )
    salary_tax_line_ids = fields.One2many(
        'hr.salary.tax.line',
        'salary_tax_id'
    )
    salary_tax_apply_ids = fields.One2many(
        'hr.salary.tax.apply.level',
        'salary_tax_id'
    )
    python_code_from_gross_to_net = fields.Text()
    python_code_from_net_to_gross = fields.Text()
    
    @api.model
    def _get_employee_taxes(self, payslip, salary_code,
                            taxable_amount, average=True):
        """
         Get Employee Taxes based on salary tax configuration
        :param payslip: Current payslip
        :param salary_code: Taxable salary rule code in s.structure
        :param taxable_amount: Current taxable amount
        :param average <Boalean>: get tax based on salary average
        :return: Tax amount
        """
        emp = self.env['hr.employee'].browse(payslip.employee_id)
        # Get current year employees' payslips
        payslips = self.env['hr.payslip']._get_year_payslip(
            emp, payslip.salary_tax_id)
        # Calculate current year employees' taxable amount
        payslips_salary = taxable_amount
        # Compute salary tax based on year salary average
        if average:
            payslips_salary = \
                payslips._get_salary_line_total(salary_code) + taxable_amount
            num_of_months = len(payslips) + 1
            payslips_salary = payslips_salary / num_of_months
        taxable_amount = payslips_salary * 12
        # Get salary tax rule
        tax = self.search(
            [('period_month_ids.name', '=', payslip.payslip_month)], limit=1)
        if not tax:
            raise UserError(_('There is no salary tax record configured'))
        tax_amount = 0
        # apply rounding to taxable amount
        rounding_method = getattr(math, tax.rounding_method)
        rounding = tax.rounding if tax.rounding else 1
        taxable_amount = rounding_method(taxable_amount / rounding) * rounding
        taxable_amount -= tax.exemption
        # @formatter:off
        apply_on = tax.salary_tax_apply_ids.filtered(
            lambda r: r.salary_from <= taxable_amount and
            taxable_amount <= r.salary_to
        )
        level = apply_on.level
        # Get sum of previous level line_amount to be added
        # to the first equation then reset it to 0
        previous_amount = sum(tax.salary_tax_line_ids.filtered(
            lambda r: r.level < level).mapped('line_amount'))
        for line in tax.salary_tax_line_ids.filtered(
                lambda r: r.level >= level):
            if taxable_amount > line.line_amount:
                tax_amount += \
                    (line.line_amount + previous_amount) * \
                    (line.tax_percentage / 100)
                taxable_amount -= (line.line_amount + previous_amount)
                previous_amount = 0
            else:
                tax_amount += taxable_amount * (line.tax_percentage / 100)
                # apply refund on taxes
                tax_amount -= (tax_amount * (line.refund_percentage / 100))
                return tax_amount / 12
        raise UserError(_('Salary tax does not cover salary amount'))

    @api.model
    def _get_employee_taxes_reconcile(self, payslip, tax_code,
                                      tax_reconcile_code, tax_amount):
        """
        Get Employee Taxes based on salary tax configuration
        :param payslip: Current payslip
        :param tax_code: Tax rule code in s.structure
        :param tax_reconcile_code: Tax reconcile rule code in s.structure
        :param tax_amount: Current payslip tax amount
        :return: Tax reconcile amount
        """
        emp = self.env['hr.employee'].browse(payslip.employee_id)
        # Get employee year payslips
        payslips = self.env['hr.payslip']._get_year_payslip(
            emp, payslip.salary_tax_id)
        # Get employee year payslips previous paid taxes
        payslips_taxes = \
            (payslips._get_salary_line_total(tax_code) +
             payslips._get_salary_line_total(tax_reconcile_code))
        # (tax_amount) current tax amount
        # (tax_amount * num_of_months) tax should pay till now
        # (payslips_taxes) previous paid taxes
        # reconcile equation :
        #   ((tax should pay till now) - (previous paid taxes)) - current tax
        num_of_months = len(payslips) + 1
        return (tax_amount * num_of_months - payslips_taxes) - tax_amount
