""" HR TNA Set Provider """
from odoo import fields, models


# pylint: disable=cell-var-from-loop,consider-using-ternary
class HrTnaSetProvider(models.TransientModel):
    """ HR TNA Set Provider """
    _name = 'hr.tna.set.provider'
    _description = 'TNA Set Provider'

    def _default_course_ids(self):
        """ get default course_provider_lines_ids """
        active_ids = self._context.get('active_model') == 'hr.tna.line' and \
            self._context.get('active_ids') or []
        tna_lines = self.env['hr.tna.line'].browse(active_ids)
        lines = []
        for course in tna_lines.mapped('course_id'):
            tna_lines_ids = tna_lines.filtered(lambda r: r.course_id == course)
            lines.append((0, 0, {
                'course_id': course.id,
                'no_of_participants': sum(
                    tna_lines_ids.mapped('no_of_participants')),
                'hr_tna_line_ids': tna_lines_ids.ids
            }))
        return lines

    course_provider_lines_ids = fields.One2many(
        'course.provider.lines', 'set_provider_id', default=_default_course_ids
    )

    def set_provider(self):
        """ Set Provider """
        for line in self.course_provider_lines_ids:
            for tna_line in line.hr_tna_line_ids:
                if tna_line.state == 'submitted':
                    tna_line.provider_id = line.provider_id.id


class CourseProviderLines(models.TransientModel):
    """ Course Provider Lines """
    _name = 'course.provider.lines'
    _description = 'Course Provider Lines'

    set_provider_id = fields.Many2one('hr.tna.set.provider')
    course_id = fields.Many2one('hr.course', readonly=True)
    hr_tna_line_ids = fields.Many2many('hr.tna.line')
    provider_id = fields.Many2one(
        'hr.course.provider.line',
        domain="[('course_id', '=', course_id)]",
    )
    no_of_participants = fields.Integer()
    minimum_no_of_participants = fields.Integer(
        related='provider_id.minimum_no_of_participants'
    )
