"""update object hr.contract"""
from odoo import api, fields, models


class HrContract(models.Model):
    """update object hr.contract"""
    _inherit = 'hr.contract'

    lines_ids = fields.One2many(
        'salary.input.line',
        'contract_id',
        string='Input Lines'
    )

    # pylint: disable=no-member
    @api.model
    def get_salary_inputs(self, date_from, codes=None):
        """ Get Sum Of Salary Input Lines"""
        domain = [('contract_id', '=', self.id)]
        if codes:
            domain.append(('code', 'in', codes))
        if date_from:
            domain += [
                '|',
                ('date_from', '=', False),
                '&',
                ('date_from', '<=', date_from),
                ('date_to', '>=', date_from)
            ]
        # based on the date from overlapping constrain it must not get an
        # input lines with the same input.
        input_data = self.env['salary.input.line'].search(domain)
        return sum(line.value for line in input_data)
