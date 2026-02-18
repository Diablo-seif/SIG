""" init object hr.attendance.interval """

from odoo import api, fields, models


# pylint: disable=unused-argument
class HrAttendanceInterval(models.Model):
    """ init object hr.attendance.interval """
    _description = 'HR Attendance Interval'

    _name = 'hr.attendance.interval'

    @api.depends('delay_in', 'record_id', 'record_id.resource_calendar_id')
    def _compute_penalty_in_id(self):
        """
        Compute Penalty In Rule.
        """
        penalty_obj = self.env['hr.penalty.rule']
        for rec in self:
            calendar_id = None
            if rec.record_id and rec.record_id.resource_calendar_id:
                calendar_id = rec.record_id.resource_calendar_id
            if calendar_id and rec.delay_in and rec.delay_in > 0:
                rec.penalty_in_id = penalty_obj.search([
                    ('delay_from', '<=', rec.delay_in),
                    ('delay_to', '>=', rec.delay_in),
                    ('calendar_id', '=', calendar_id.id),
                    ('penalty_type', '=', "late_in"),
                ], limit=1)

    @api.depends('delay_in', 'record_id', 'record_id.resource_calendar_id')
    def _compute_penalty_out_id(self):
        """
        Compute Penalty Out Rule.
        """
        penalty_obj = self.env['hr.penalty.rule']
        for rec in self:
            calendar_id = None
            if rec.record_id and rec.record_id.resource_calendar_id:
                calendar_id = rec.record_id.resource_calendar_id
            if calendar_id and rec.early_out and rec.early_out > 0:
                rec.penalty_out_id = penalty_obj.search([
                    ('delay_from', '<=', rec.early_out),
                    ('delay_to', '>=', rec.early_out),
                    ('calendar_id', '=', calendar_id.id),
                    ('penalty_type', '=', "early_out"),
                ], limit=1)

    @api.depends('missing_hours', 'record_id', 'record_id.resource_calendar_id')
    def _compute_penalty_missing_id(self):
        """
        Compute Penalty Missing Hours Rule.
        """
        penalty_obj = self.env['hr.penalty.rule']
        for rec in self:
            calendar_id = None
            if rec.record_id and rec.record_id.resource_calendar_id:
                calendar_id = rec.record_id.resource_calendar_id
            if calendar_id and rec.missing_hours and rec.missing_hours > 0:
                rec.penalty_missing_id = penalty_obj.search([
                    ('delay_from', '<=', rec.missing_hours * 60),
                    ('delay_to', '>=', rec.missing_hours * 60),
                    ('calendar_id', '=', calendar_id.id),
                    ('penalty_type', '=', "missing_hours"),
                ], limit=1)

    @api.depends('penalty_in_redundant', 'penalty_in_id')
    def _compute_penalty_in_percentage(self):
        """
        Compute Penalty In Value.
        """
        for rec in self:
            if rec.penalty_in_redundant and rec.penalty_in_redundant > 0 \
                    and rec.penalty_in_id:
                if rec.penalty_in_id.deduction_type == 'percentage':
                    rec.penalty_in_percentage = rec.penalty_in_id. \
                        get_penalty_value_redundant(rec.penalty_in_redundant)
                if rec.penalty_in_id.deduction_type == 'fixed_amount':
                    rec.penalty_in_amount = rec.penalty_in_id. \
                        get_penalty_value_redundant(rec.penalty_in_redundant)

    @api.depends('penalty_out_redundant', 'penalty_out_id')
    def _compute_penalty_out_percentage(self):
        """
        Compute Penalty Out Value.
        """
        for rec in self:
            if rec.penalty_out_redundant and rec.penalty_out_redundant > 0 \
                    and rec.penalty_out_id:
                if rec.penalty_out_id.deduction_type == 'percentage':
                    rec.penalty_out_percentage = rec.penalty_out_id. \
                        get_penalty_value_redundant(rec.penalty_out_redundant)
                if rec.penalty_out_id.deduction_type == 'fixed_amount':
                    rec.penalty_out_amount = rec.penalty_out_id. \
                        get_penalty_value_redundant(rec.penalty_out_redundant)

    @api.depends('penalty_missing_redundant', 'penalty_missing_id')
    def _compute_penalty_missing_percentage(self):
        """
        Compute Penalty Missing Hours Value.
        """
        for rec in self:
            if rec.penalty_missing_redundant \
                    and rec.penalty_missing_redundant > 0 \
                    and rec.penalty_missing_id:
                if rec.penalty_missing_id.deduction_type == 'percentage':
                    rec.penalty_missing_percentage = rec.penalty_missing_id. \
                        get_penalty_value_redundant(rec.
                                                    penalty_missing_redundant)
                if rec.penalty_missing_id.deduction_type == 'fixed_amount':
                    rec.penalty_missing_amount = rec.penalty_missing_id. \
                        get_penalty_value_redundant(rec.
                                                    penalty_missing_redundant)

    # pylint: disable=cell-var-from-loop
    @api.depends('is_attend', 'absent_redundant', 'record_id',
                 'record_id.resource_calendar_id',
                 'record_id.resource_calendar_id.absent_ids')
    def _compute_absent_value(self):
        """
        Compute absent Value.
        """
        for rec in self:
            absent_value = 0
            absent_ids = rec.record_id.resource_calendar_id.absent_ids
            if not rec.is_attend and rec.absent_redundant and \
                    rec.record_id.resource_calendar_id and absent_ids:
                absent_id = absent_ids.filtered(
                    lambda cls: cls.redundant == rec.absent_redundant)
                if not absent_id:
                    less_absent_ids = absent_ids.filtered(
                        lambda cls: cls.redundant < rec.absent_redundant)
                    if less_absent_ids:
                        absent_id = less_absent_ids[-1]
                if absent_id:
                    absent_value = absent_id[0].absent_value
            rec.absent_value = absent_value

    record_id = fields.Many2one(comodel_name="hr.attendance.record",
                                ondelete="set null")
    name = fields.Char(string="Data", required=False)
    start_datetime = fields.Datetime()
    end_datetime = fields.Datetime()
    allow_form_datetime = fields.Datetime()
    allow_to_datetime = fields.Datetime()
    delay_in = fields.Integer()
    penalty_in_redundant = fields.Integer()
    penalty_in_id = fields.Many2one(comodel_name="hr.penalty.rule", store=True,
                                    compute=_compute_penalty_in_id)
    early_out = fields.Integer()
    penalty_out_redundant = fields.Integer()
    penalty_out_id = fields.Many2one(comodel_name="hr.penalty.rule", store=True,
                                     compute=_compute_penalty_out_id)
    penalty_in_percentage = fields.Float(store=True,
                                         compute=_compute_penalty_in_percentage)
    penalty_in_amount = fields.Float(store=True,
                                     compute=_compute_penalty_in_percentage)
    penalty_out_percentage = fields.Float(
        store=True,
        compute=_compute_penalty_out_percentage)
    penalty_out_amount = fields.Float(store=True,
                                      compute=_compute_penalty_out_percentage)
    is_attend = fields.Boolean()
    absent_redundant = fields.Integer()
    absent_value = fields.Float(store=True, compute=_compute_absent_value)
    actual_working_hours = fields.Float()
    working_hours = fields.Float()
    min_hours_attend = fields.Float()
    missing_hours = fields.Float()
    penalty_missing_redundant = fields.Integer()
    penalty_missing_id = fields.Many2one(comodel_name="hr.penalty.rule",
                                         string="Penalty Missing Hours",
                                         store=True,
                                         compute=_compute_penalty_missing_id)
    penalty_missing_percentage = fields.Float(
        store=True, string="Penalty Missing Hours Percentage",
        compute=_compute_penalty_missing_percentage)
    penalty_missing_amount = fields.Float(
        store=True, string="Penalty Missing Hours Amount",
        compute=_compute_penalty_missing_percentage)
