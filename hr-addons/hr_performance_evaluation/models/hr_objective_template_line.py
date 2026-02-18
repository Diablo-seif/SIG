""" init hr.objective.template.line """

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


# pylint: disable=no-member,protected-access
class HrObjectiveTemplateLine(models.Model):
    """
        init hr.objective.template.line:
    """
    _name = 'hr.objective.template.line'
    _description = 'HR Objective Template Line'
    _order = 'sequence, id'

    template_id = fields.Many2one(
        comodel_name='hr.performance.template',
        ondelete='cascade',
    )
    name = fields.Char(
        string='Key Objective Area',
        required=True,
    )
    description = fields.Text()
    hint = fields.Char()
    weightage = fields.Float()
    sequence = fields.Integer(
        default=10,
    )
    display_type = fields.Selection(
        selection=[
            ('line_section', "Section")],
        default=False,
        help="Technical field for UX purpose.",
    )

    @api.constrains('weightage')
    def _check_weightage(self):
        """
        restrict negative
        """
        for record in self:
            if record.weightage < 0:
                raise ValidationError(_('Please add negative amount for %s!')
                                      % record.name)
