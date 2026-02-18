""" Update object hr.payslip.run """

from odoo import fields, models


class HrPayslipRun(models.Model):
    """ Update object hr.payslip.run """
    _inherit = "hr.payslip.run"

    def _get_default_date_start(self):
        """
        Get Default date_start like date_from in payslip.
        :return: date_start <Date>
        """
        # pylint: disable=protected-access
        return self.env['hr.payslip']._get_default_date_from()

    def _get_default_date_end(self):
        """
        Get Default date_end like date_to in payslip.
        :return: date_end <Date>
        """
        # pylint: disable=protected-access
        return self.env['hr.payslip']._get_default_date_to()

    date_start = fields.Date(default=_get_default_date_start)
    date_end = fields.Date(default=_get_default_date_end)
