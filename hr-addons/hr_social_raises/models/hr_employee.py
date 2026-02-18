""" HR Employee """

from odoo import api, fields, models


class HrEmployee(models.AbstractModel):
    """ inherit HR Employee Base to add raises field"""
    _inherit = 'hr.employee.base'

    raises_ids = fields.One2many(
        'hr.social.raises',
        'employee_id'
    )
    total_raises = fields.Float(
        compute='_compute_total_raises',
        compute_sudo=True,
        store=True
    )

    @api.depends('raises_ids', 'raises_ids.raise_amount')
    def _compute_total_raises(self):
        """ Compute total_raises value """
        for rec in self:
            rec.total_raises = sum(self.env['hr.social.raises'].search(
                [('employee_id', '=', rec.id)], order='name desc', limit=5
            ).mapped('raise_amount'))
