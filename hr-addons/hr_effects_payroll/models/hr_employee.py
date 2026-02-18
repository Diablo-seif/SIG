""" update object employee to add function"""

from odoo import models, api


class HrEmployee(models.Model):
    """ update object employee to add function"""
    _inherit = 'hr.employee'

    # pylint: disable=no-member
    @api.model
    def get_effects_payroll(self, effects_category, dateform=None,
                            dateto=None, code=None):
        """
        Function to get effects salary.
        :param <string> effects_category: additions/deductions
        :param dateform:
        :param dateto:
        :param <string> (optional) code: effects type code
        :return: <float> total value
        """
        value = 0
        if effects_category and dateform and dateto and self.id:
            effects_payroll_obj = self.env['hr.effects.payroll']
            domain = [
                ('employee_id', '=', self.id),
                ('effective_date', '>=', dateform),
                ('effective_date', '<=', dateto),
                ('effects_category', '=', effects_category),
                ('state', '=', 'approved'),
            ]
            if code:
                domain.append(('effects_type_id.code', '=', code))
            effects_payroll_data = effects_payroll_obj.search(domain)
            value = sum(effects_payroll_data.mapped('value'))
            if effects_category == 'deductions':
                value = value * -1
        return value
