""" Initialize Hr Performance Score Scale """

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


# pylint: disable=no-member,protected-access
class HrPerformanceScoreScale(models.Model):
    """
        init hr.performance.score.scale:
    """
    _name = 'hr.performance.score.scale'
    _description = 'HR Performance Score Scale'
    _check_company_auto = True
    _order = 'score_from'

    name = fields.Char(
        required=True,
    )
    active = fields.Boolean(
        default=True,
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        default=lambda self: self.env.company,
    )
    score_from = fields.Float()
    score_to = fields.Float()

    @api.constrains('score_from', 'score_to')
    def _check_scores(self):
        """ Validate scores to prevent overlaps """
        for record in self:
            start = record.score_from
            end = record.score_to
            overlaps = self.search([
                ('id', '!=', record.id), '|', '&',
                ('score_from', '<', start), ('score_to', '>', start), '&',
                ('score_from', '<', end), ('score_to', '>', end),
            ])
            if overlaps:
                raise ValidationError(_("Scores is overlapped"))
