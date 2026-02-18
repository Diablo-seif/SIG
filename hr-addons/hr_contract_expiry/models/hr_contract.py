""" update object hr.contract """

from datetime import date

from dateutil.relativedelta import relativedelta

from odoo import fields, models


class HrContract(models.Model):
    """ update object hr.contract """
    _inherit = 'hr.contract'

    def _compute_alert_number(self):
        """
        Function To compute alert_number
        Note:
        alert_number=2,1 decoration-warning
        alert_number=3 decoration-danger
        alert_number=9 decoration-info
        alert_number=10 decoration-success
        else normal
        :return:
        """
        now_date = date.today()
        for rec in self:
            alert_number = 0
            if rec.date_end:
                before3months = rec.date_end + relativedelta(months=-3)
                before2months = rec.date_end + relativedelta(months=-2)
                before1months = rec.date_end + relativedelta(months=-1)
                if before1months <= now_date <= rec.date_end:
                    alert_number = 1
                elif before2months <= now_date <= rec.date_end:
                    alert_number = 2
                elif before3months <= now_date <= rec.date_end:
                    alert_number = 3
                elif rec.date_end > now_date:
                    alert_number = 9
            else:
                alert_number = 10
            rec.alert_number = alert_number

    alert_number = fields.Integer(default=0, compute=_compute_alert_number)
