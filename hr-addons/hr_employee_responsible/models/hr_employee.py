""" HR Employee """

from odoo import fields, models


class HrEmployee(models.Model):
    """ inherit HR Employee to add responsible """
    _inherit = 'hr.employee'

    hr_user_id = fields.Many2one(
        'res.users',
        string='HR Responsible',
        groups="hr.group_hr_user",  # to avoid using in employee public
        domain=lambda self: [
            ('groups_id', '=', self.env.ref('hr.group_hr_user').id)]
    )
