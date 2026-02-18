""" Update object hr.contract """

from odoo import _, api, models
from odoo.exceptions import UserError


class HrContract(models.Model):
    """ Update object hr.contract """

    _inherit = "hr.contract"

    # pylint: disable=no-member, bad-continuation
    @api.constrains('date_start', 'date_end', 'employee_id', 'active')
    def _constrains_contract_overlaps(self):
        """
        Funcion constrains contract overlaps
        :return:
        """
        for contract in self:
            if contract.employee_id:
                domain = []
                if contract.date_start and contract.date_end:
                    domain = [
                        '&', '|', '&', ('date_start', '<=', contract.date_end),
                        ('date_end', '>=', contract.date_start),
                        '&', ('date_end', '=', False),
                        '|', '&', ('date_start', '>=', contract.date_start),
                        ('date_start', '<=', contract.date_end),
                        ('date_start', '<', contract.date_start),
                        '&', ('employee_id', '=', contract.employee_id.id),
                        ('id', '!=', contract.id)
                    ]

                elif contract.date_start and not contract.date_end:
                    domain = [
                        '&', '|', ('date_end', '=', False),
                        ('date_end', '>=', contract.date_start),
                        '&', ('employee_id', '=', contract.employee_id.id),
                        ('id', '!=', contract.id)
                    ]
                if domain:
                    count_contracts = self.search_count(domain)
                    if count_contracts:
                        raise UserError(_('You can not have 2 contract that '
                                          'overlaps on same day'))
