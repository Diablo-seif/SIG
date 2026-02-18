""" init object hr.leave"""

from odoo import fields, models


class HrHolidays(models.Model):
    """ init object hr.leave"""
    _inherit = 'hr.leave'

    def create_expense_leave(self):
        """
        Action Create expense Leave.
        """
        for leave in self:
            if leave.holiday_status_id \
                    and leave.employee_id \
                    and leave.holiday_type in ['employee'] \
                    and leave.holiday_status_id.link_to_expenses \
                    and leave.holiday_status_id.leave_expense_ids:
                leave_name = "[#%d]" % leave.id
                if leave.name:
                    leave_name = leave.display_name
                expenses_vals = []
                for line in leave.holiday_status_id.leave_expense_ids:
                    # pylint: disable=protected-access
                    employees = line._get_employees()
                    if leave.employee_id in employees:
                        vals = {
                            'name': "Expense For Time Off: %s" % leave_name,
                            'employee_id': leave.employee_id.id,
                            'product_id': line.product_id.id,
                            'product_uom_id': line.product_id.uom_id.id,
                            'unit_amount': line.unit_amount,
                            'quantity': leave.number_of_days,
                            'extract_state': 'no_extract_requested',
                            'currency_id': line.currency_id.id,
                            'company_id': line.company_id.id,
                        }
                        if line.analytic_account_id:
                            vals.update(
                                analytic_account_id=line.analytic_account_id.id
                            )
                        expenses_vals.append(vals)
                if expenses_vals:
                    sheet_vals = {
                        'name': "Expense Sheet For Time Off: %s" % leave_name,
                        'employee_id': leave.employee_id.id,
                        'leave_id': leave.id,
                    }
                    if leave.employee_id.parent_id and \
                            leave.employee_id.parent_id.user_id:
                        sheet_vals.update(
                            user_id=leave.employee_id.parent_id.user_id.id
                        )
                    sheet_id = self.env['hr.expense.sheet'].create(sheet_vals)
                    for vals in expenses_vals:
                        vals['sheet_id'] = sheet_id.id
                        self.env['hr.expense'].create(vals)
                    sheet_id.action_submit_sheet()
                    leave.sheet_id = sheet_id.id
                    return {
                        'type': 'ir.actions.act_window',
                        'view_mode': 'form',
                        'res_model': 'hr.expense.sheet',
                        'target': 'current',
                        'res_id': sheet_id.id
                    }
        return False

    # pylint: disable=no-member
    def action_validate(self):
        """
        Override Action Validate To Add Expense Related To this Leave Type.
        """
        res = super(HrHolidays, self).action_validate()
        for leave in self:
            if leave.holiday_status_id and \
                    leave.holiday_status_id.leave_validation_type == 'both':
                expense_leave = leave.create_expense_leave()
                if expense_leave:
                    return expense_leave
            return res

    # pylint: disable=no-member
    def action_approve(self):
        """
        Override Action Approve To Add Expense Related To this Leave Type.
        """
        res = super(HrHolidays, self).action_approve()
        for leave in self:
            if leave.holiday_status_id and \
                    not leave.holiday_status_id.leave_validation_type == 'both':
                expense_leave = self.create_expense_leave()
                if expense_leave:
                    return expense_leave
        return res

    sheet_id = fields.Many2one("hr.expense.sheet", string="Expense Sheet", )
