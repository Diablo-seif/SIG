""" init object hr.leave to fix issue """

from odoo import _, api, models
from odoo.exceptions import ValidationError


class HrLeave(models.Model):
    """ init object hr.leave to fix issue """

    _inherit = 'hr.leave'

    @api.constrains('date_from', 'date_to', 'state', 'employee_id')
    def _check_date(self):
        """
        Override Function _check_date to fix Issue.
        Old code `('date_to', '>', holiday.date_from)`
        New code `('date_to', '>=', holiday.date_from)`
        """
        for holiday in self:
            if holiday.employee_id:
                domain = [
                    ('date_from', '<=', holiday.date_to),
                    ('date_to', '>=', holiday.date_from),
                    ('employee_id', '=', holiday.employee_id.id),
                    ('id', '!=', holiday.id),
                    ('state', 'not in', ['cancel', 'refuse']),
                ]
                holidays_count = self.search_count(domain)
                if holidays_count:
                    raise ValidationError(_(
                        'You can not have 2 leaves that '
                        'overlaps on the same day.'
                    ))
