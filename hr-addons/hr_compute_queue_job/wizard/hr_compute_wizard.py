""" init object hr.compute.wizard """

from odoo import fields, models, _
from odoo.exceptions import UserError

MODULE = 'hr.compute.attendance.line'


class HrComputeWizard(models.TransientModel):
    """ init object hr.compute.wizard """

    _name = 'hr.compute.wizard'
    _description = 'Attendnace Compute Wizard'

    def get_active_lines(self):
        """
        Get Active Lines
        :return:
        """
        context = self.env.context.copy()
        if 'active_model' in context and 'active_model' in context \
                and context.get('active_model', '') == MODULE \
                and context.get('active_ids', ''):
            return self.env[MODULE].browse(context.get('active_ids'))
        raise UserError(_('Error!!\nCannot Get Active Compute Lines.'))

    def _default_count_selected(self):
        """
        Get Count Selected lines Form Context active_ids.
        """
        context = self.env.context.copy()
        if 'active_model' in context and 'active_model' in context \
                and context.get('active_model', '') == MODULE \
                and context.get('active_ids', ''):
            return self.env[MODULE].search_count(
                [('id', 'in', context.get('active_ids'))])
        return 0

    def action_re_schedule(self):
        """
        Action Re Schedule Active Compute Lines.
        """
        self.ensure_one()
        for line in self.get_active_lines():
            line.re_progress()

    count_selected = fields.Integer(default=_default_count_selected)
