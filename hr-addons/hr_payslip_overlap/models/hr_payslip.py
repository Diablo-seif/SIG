""" Update object hr.payslip """

from odoo import _, api, models
from odoo.exceptions import UserError


class HrPayslip(models.Model):
    """ Update object hr.payslip """
    _inherit = "hr.payslip"

    @api.constrains('employee_id', 'date_from', 'date_to')
    def _check_date_with_employee(self):
        """
        Function to check overlaps
        :return:
        """
        for payslip in self:
            domain = [('date_from', '<=', payslip.date_to),
                      ('date_to', '>=', payslip.date_from),
                      ('employee_id', '=', payslip.employee_id.id),
                      ('id', '!=', payslip.id)]
            payslips_count = self.search_count(domain)
            if payslips_count:
                msg = "You cannot have two payslips that overlap " \
                      "in duration for the same Employee."
                raise UserError(_(msg))
