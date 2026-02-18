""" init object hr.dynamic.service.subtype"""

from odoo import fields, models


# pylint: disable=no-member
class HrServiceSubtype(models.Model):
    """ init object hr.dynamic.service.subtype"""
    _name = 'hr.dynamic.service.subtype'
    _rec_name = 'name'
    _description = 'Dynamic Approval Subtype'
    _order = 'sequence asc, id asc'

    def _get_default_sequence(self):
        """
        Get next sequence subtype.
        :return:
        """
        res = 1
        service_type_id = self.env.context.get('service_type_id', 0)
        service_subtype = self.search(
            [('service_type_id', '=', service_type_id)], limit=1,
            order='sequence desc'
        )
        if service_subtype:
            res = service_subtype.sequence + 1
        return res

    def _compute_service_count(self):
        """
        Compute Service Count By User
        """
        for rec in self:
            rec.service_count = self.env['hr.dynamic.service'].search_count(
                [('employee_id.user_id', '=', self.env.user.id),
                 ('service_subtype_id', '=', rec.id)]
            )

    def _compute_service_draft_count(self):
        """
        Compute Service Draft Count By User
        """
        for rec in self:
            rec.service_draft_count = \
                self.env['hr.dynamic.service'].search_count([
                    ('employee_id.user_id', '=', self.env.user.id),
                    ('is_first_stage', '=', True),
                    ('service_subtype_id', '=', rec.id)])

    def _compute_service_progress_count(self):
        """
        Compute Service Draft Count By User
        """
        for rec in self:
            # @formatter:off
            rec.service_progress_count = self.env[
                'hr.dynamic.service'].search_count([
                    ('employee_id.user_id', '=', self.env.user.id),
                    ('is_first_stage', '=', False),
                    ('next_stage_id', '!=', False),
                    ('service_subtype_id', '=', rec.id)
                ])

    def _compute_service_done_count(self):
        """
        Compute Service Done Count By User
        """
        service_obj = self.env['hr.dynamic.service']
        for rec in self:
            rec.service_done_count = service_obj.search_count([
                ('employee_id.user_id', '=', self.env.user.id),
                ('next_stage_id', '=', False),
                ('service_subtype_id', '=', rec.id)])

    def open_request_action(self, action_type=None):
        """
        open_request_action
        :param action_type:
        :return: action
        """
        self.ensure_one()
        employee_id = False
        employee_ids = self.env.user.employee_ids
        if employee_ids:
            employee_id = employee_ids[0].id
        ctx = self.env.context.copy()
        ctx.update({
            'search_default_employee_id': employee_id,
            'default_employee_id': employee_id,
            'search_default_service_type_id': self.service_type_id.id,
            'search_default_service_subtype_id': self.id,
            'default_service_type_id': self.service_type_id.id,
            'default_service_subtype_id': self.id,
        })
        if action_type == 'draft':
            ctx.update({'search_default_request_draft': 1})
        elif action_type == 'progress':
            ctx.update({'search_default_request_progress': 1})
        elif action_type == 'done':
            ctx.update({'search_default_request_done': 1})
        action = self.env.ref('hr_dynamic_service.view_hr_'
                              'dynamic_service_action').sudo().read()[0]
        if action_type:
            action['name'] = " my requests "
        action['context'] = ctx
        return action

    def action_open_draft_requests(self):
        """
        Action Open Draft Requests
        """
        self.ensure_one()
        return self.open_request_action('draft')

    def action_open_progress_requests(self):
        """
        Action Open progress Requests
        """
        self.ensure_one()
        return self.open_request_action('progress')

    def action_open_done_requests(self):
        """
        Action Open progress Requests
        """
        self.ensure_one()
        return self.open_request_action('done')

    service_type_id = fields.Many2one(
        comodel_name="hr.dynamic.service.type", string="Service Type"
    )
    sequence = fields.Integer(default=_get_default_sequence)
    name = fields.Char(string="Subtype Name", translate=True, required=True)
    service_count = fields.Integer(compute=_compute_service_count)
    service_draft_count = fields.Integer(compute=_compute_service_draft_count)
    service_progress_count = fields.Integer(
        compute=_compute_service_progress_count)
    service_done_count = fields.Integer(compute=_compute_service_done_count)
