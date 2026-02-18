""" init object hr.leave.expense"""

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp
from odoo.osv import expression


class HrLeaveExpense(models.Model):
    """ init object hr.leave.expense"""
    _name = 'hr.leave.expense'
    _description = 'HR Time Off Expense line'

    @api.model
    def _default_product_uom_id(self):
        """
        Get default Product UOM.
        :return: <uom.uom> uom_id
        """
        return self.env['uom.uom'].search([], limit=1, order='id')

    def _get_employees(self):
        """
        Get Employees.
        :return: <hr.employee> employee_ids
        """
        employees = self.env['hr.employee']
        domain = []
        for line in self:
            if line.employee_ids:
                domain.append([('id', 'in', line.employee_ids.ids)])
            if line.department_ids:
                domain.append(
                    [('department_id', 'in', line.department_ids.ids)])
            if line.job_ids:
                domain.append([('job_id', 'in', line.job_ids.ids)])
            if line.employee_category_ids:
                domain.append(
                    [('category_ids', 'in', line.employee_category_ids.ids)])
            if domain:
                domain = expression.OR(domain)
            employees |= employees.search(domain)
        return employees

    leave_type_id = fields.Many2one("hr.leave.type", string="Time Off Type")
    employee_ids = fields.Many2many(
        "hr.employee", relation="leave_type_employee_rel",
        column1="leave_type_id", column2="employee_id", string="Employees")
    department_ids = fields.Many2many(
        "hr.department", relation="leave_type_department_rel",
        column1="leave_type_id", column2="department_id", string="Departments")
    employee_category_ids = fields.Many2many(
        "hr.employee.category", relation="leave_type_employee_category_rel",
        column1="leave_type_id", column2="employee_category_id",
        string="Employee Tags", )
    job_ids = fields.Many2many(
        "hr.job", relation="leave_type_job_rel", column1="leave_type_id",
        column2="job_id", string="Job Positions")
    product_id = fields.Many2one('product.product', required=True,
                                 domain=[('can_be_expensed', '=', True)])
    product_uom_id = fields.Many2one(
        'uom.uom', string='Unit of Measure', required=True,
        default=_default_product_uom_id)
    unit_amount = fields.Float(
        "Unit Price", required=True, digits=dp.get_precision('Product Price'))
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id)
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company.id)
    analytic_account_id = fields.Many2one('account.analytic.account')

    _sql_constraints = [('unit_amount_gt_zero',
                         'CHECK (unit_amount>=0)',
                         'Please add positive unit price.'), ]
