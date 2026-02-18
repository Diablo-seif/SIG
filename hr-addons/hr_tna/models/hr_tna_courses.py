""" HR TNA Courses """
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HrTnaCourses(models.Model):
    """ HR Tna Courses """
    _name = 'hr.tna.courses'
    _description = 'TNA Courses'

    name = fields.Char(default='New')
    state = fields.Selection([
        ('pending', 'Pending'), ('running', 'Running'), ('done', 'Done'),
    ], readonly=True, default='pending', group_expand='_group_expand_state')
    employee_id = fields.Many2one('hr.employee', required=True)
    course_id = fields.Many2one(related='tna_line_id.course_id', store=True)
    estimated_date = fields.Date(string='Estimated Start Date')
    tna_line_id = fields.Many2one('hr.tna.line', ondelete='cascade')

    # pylint: disable=unused-argument
    def _group_expand_state(self, states, domain, order):
        """ Expand kanban columnes for stat """
        return [key for key, val in type(self).state.selection]

    @api.model
    def create(self, vals_list):
        """ Override create method to sequence name """
        if vals_list.get('name', 'New'):
            vals_list['name'] = self.env['ir.sequence'].next_by_code(
                'tna.courses') or '/'
        return super().create(vals_list)

    @api.constrains('estimated_date')
    def _check_estimated_date(self):
        """ Validate estimated_date not to exceed overall TNA end date """
        for line in self:
            plan_from = line.tna_line_id.tna_id.date_from
            plan_to = line.tna_line_id.tna_id.date_to
            if line.estimated_date:
                if line.estimated_date < plan_from or \
                        line.estimated_date > plan_to:
                    raise ValidationError(
                        _('Estimated Starting Date '
                          'must be between %(plan_from)s '
                          'and %(plan_to)s') % {
                              "plan_from": plan_from,
                              "plan_to": plan_to}
                    )
