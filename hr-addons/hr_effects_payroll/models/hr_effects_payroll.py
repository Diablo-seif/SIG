""" init object hr.effects.payroll """

from odoo import _, fields, models
from odoo.exceptions import UserError


class HrEffectsPayroll(models.Model):
    """ init object hr.effects.payroll """

    _name = 'hr.effects.payroll'
    _description = "Hr Payroll Effects"

    _sql_constraints = [
        ('positive_value', 'CHECK(value>0)', 'Value must be positive')
    ]

    employee_id = fields.Many2one("hr.employee", required=True)
    effects_category = fields.Selection(
        [('additions', 'Additions'), ('deductions', 'Deductions')])
    effects_type_id = fields.Many2one(
        "hr.effects.payroll.type", string="Type", required=True, )
    effective_date = fields.Date(required=True)
    value = fields.Float(required=True)
    state = fields.Selection(
        [('draft', 'Draft'), ('approved', 'Approved')],
        string="Status", default='draft')
    note = fields.Text()

    def name_get(self):
        """
        Override name_get
        to concatenate effects_category effects_type employee_name id
        """
        result = []
        for rec in self:
            result.append((rec.id, "%s %s %s (%d)" %
                           (rec.effects_category,
                            rec.effects_type_id.name,
                            rec.employee_id.name,
                            rec.id)))
        return result

    def unlink(self):
        """
        Override unlink to restrict approved
        """
        for record in self:
            if record.state == 'approved':
                effects_category_str = 'Deductions'
                if record.effects_category == 'additions':
                    effects_category_str = 'Additions'
                raise UserError(
                    _('You Cannot Delete %(effects_category_str)s '
                      'in State Approved.')
                    % ({'effects_category_str': effects_category_str}))
        return super(HrEffectsPayroll, self).unlink()

    def action_approve(self):
        """
        Action approved
        """
        self.update({'state': "approved"})

    def action_draft(self):
        """
        Action set draft
        """
        self.update({'state': "draft"})
