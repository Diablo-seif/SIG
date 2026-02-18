""" HR Employee """

import logging
import math

from odoo import models

LOGGER = logging.getLogger(__name__)


class HrEmployee(models.Model):
    """ inherit HR Employee """
    _inherit = 'hr.employee'

    def get_insurance_salary(self, method, amount, round_value, date):
        """ Update Insurance Salary """
        for rec in self:
            emp_salary = rec.insured_salary
            salary = emp_salary + amount if method == 'fixed' else \
                emp_salary + emp_salary * (amount / 100)
            if round_value:
                salary = math.ceil(salary / round_value) * round_value
            config = self.env['social.insurance.config'].search([
                ('date_from', '<=', date),
                ('date_to', '>=', date)
            ], limit=1)
            if config:
                if config.min_value:
                    salary = max(config.min_value, salary)
                if config.max_value:
                    salary = min(config.max_value, salary)
            else:
                LOGGER.warning('There is no insurance configuration to apply')
            return salary
