""" init object hr.attendance"""

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class HrAttendance(models.Model):
    """ init object hr.attendance"""
    _inherit = 'hr.attendance'

    @api.depends('check_in')
    def _compute_date(self):
        """
        Compute Date base on midday config.
        """
        for rec in self:
            midday_time = round(float(self.env['ir.config_parameter'].sudo().
                                      get_param('midday_time', default=0.0)), 2)
            midday_time_h = int(midday_time)
            midday_time_m = round(((midday_time - midday_time_h) * 60), 0)
            delta = relativedelta(hours=midday_time_h, minutes=midday_time_m)
            rec.date = (rec.check_in + delta).date()

    date = fields.Date(compute=_compute_date, store=True)
