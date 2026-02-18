""" init object hr.dynamic.service """

import logging

from odoo import _, api, fields, models, SUPERUSER_ID
from odoo.exceptions import UserError, AccessError
from odoo.tools.safe_eval import safe_eval

LOGGER = logging.getLogger(__name__)


# pylint: disable=no-member
class HrDynamicService(models.Model):
    """ init object hr.dynamic.service """
    _name = 'hr.dynamic.service'
    _rec_name = 'name'
    _description = 'Dynamic Approval Request'
    _inherit = ['mail.thread']

    def set_first_stage(self):
        """
        Set to first stage.
        """
        stage_obj = self.env['hr.dynamic.service.stage']
        for rec in self:
            if rec.first_stage_id:
                rec.stage_id = rec.first_stage_id.id
            else:
                if rec.service_type_id:
                    stage_data = stage_obj.search(
                        [('service_type_id', '=', rec.service_type_id.id),
                         ('stage_for_refused', '=', False)],
                        order='sequence asc', limit=1)
                    if stage_data:
                        rec.stage_id = stage_data.id

    def unlink(self):
        """
        Override unlink to raise if not available to delete.
        """
        for record in self:
            if not record.is_first_stage \
                    or not record.service_type_id.delete_in_first_stage:
                raise UserError(_('You Cannot Delete this Request.'))
        return super(HrDynamicService, self).unlink()

    @api.model
    def create(self, vals_list):
        """
        Override to set first stage as a default.
        """
        res = super(HrDynamicService, self).create(vals_list)
        if not res.stage_id:
            res.set_first_stage()
            res.run_server_action(res.stage_id)
        return res

    def run_server_action(self, next_stage_id):
        """
        run_server_action
        :param next_stage_id:
        :return:
        """
        self.ensure_one()
        if not next_stage_id or not next_stage_id.server_action_id:
            return False
        context = self.env.context.copy()
        context.update({'active_model': self._name,
                        'active_id': self.id,
                        'active_ids': [self.id]})
        try:
            return next_stage_id.sudo().server_action_id.with_context(
                **context).run()
        except AccessError as exp:
            LOGGER.exception(str(exp))
            if next_stage_id.sudo().server_action_id.state not in ['code']:
                return next_stage_id.server_action_id.with_user(
                    SUPERUSER_ID).with_context**(context).run()

    # pylint: disable=no-else-return
    def run_next_action(self):
        """
        Action move to next stage.
        """
        for rec in self:
            hr_users = self.env.ref("hr.group_hr_user").with_user(
                SUPERUSER_ID).users
            if not rec.stage_id:
                raise UserError(_('Current Stage Object Not Found. '))
            if not rec.next_stage_id:
                raise UserError(_('Next Stage Not Found. '))
            if self.env.user in rec.next_stage_user_ids \
                    or self.env.user in hr_users:
                rec.stage_id = rec.next_stage_id.id
                return rec.run_server_action(rec.stage_id)
            else:
                raise UserError(_("The requested operation cannot be completed"
                                  " due to security restrictions."))

    @api.depends('stage_id', 'first_stage_id')
    def _compute_is_first_stage(self):
        """
        Compute is first stage.
        """
        for rec in self:
            is_first_stage = False
            if rec.stage_id and rec.first_stage_id == rec.stage_id:
                is_first_stage = True
            rec.is_first_stage = is_first_stage

    @api.depends('service_type_id', 'service_type_id.stage_ids',
                 'service_type_id.stage_ids.sequence')
    def _compute_first_stage_id(self):
        """
        Compute first stage.
        """
        stage_obj = self.env['hr.dynamic.service.stage']
        for rec in self:
            if rec.service_type_id and rec.service_type_id.stage_ids:
                stages = stage_obj.search(
                    [('service_type_id', '=', rec.service_type_id.id),
                     ('stage_for_refused', '=', False)], limit=1,
                    order='sequence asc')
                if stages:
                    rec.first_stage_id = stages.id

    @api.depends('stage_id')
    def _compute_next_stage(self):
        """
        Compute next stage.
        """
        for rec in self:
            rec.next_stage_id = self.env['hr.dynamic.service.stage'].search(
                [('service_type_id', '=', rec.service_type_id.id),
                 ('sequence', '>=', rec.stage_id.sequence),
                 ('id', '>', rec.stage_id.id),
                 ('stage_for_refused', '=', False)],
                limit=1,
                order='sequence asc, id asc')

    # pylint: disable=inconsistent-return-statements
    def action_first_stage(self):
        """
        Action change to first stage.
        :return:
        """
        for rec in self:
            if rec.first_stage_id:
                rec.is_refused = False
                rec.stage_id = rec.first_stage_id
                return rec.run_server_action(rec.stage_id)

    # pylint: disable=self-cls-assignment
    def get_users_from_stage(self, stage):
        """
        Get users list from stage.
        :param stage: Object <hr.dynamic.service.stage> (Required)
        :return: list of users
        """
        # run this function as SUPERUSER_ID.
        self = self.with_user(SUPERUSER_ID)
        stage = stage.with_user(SUPERUSER_ID)
        user_ids = self.env['res.users']
        if stage and self:
            if stage.use_domain and stage.domain:
                domain = safe_eval(stage.domain)
                if 'user_id' not in stage.domain:
                    domain.append(('user_id', '!=', False))
                employees = self.env['hr.employee'].search(domain)
                for emp in employees:
                    user_ids |= emp.user_id
            if stage.his_direct_manager \
                    and self.employee_id.parent_id \
                    and self.employee_id.parent_id.user_id:
                user_ids |= self.employee_id.parent_id.user_id
            if stage.his_department_head \
                    and self.employee_id.department_id \
                    and self.employee_id.department_id.manager_id:
                dep_emp_id = self.employee_id.department_id.manager_id
                if dep_emp_id.user_id:
                    user_ids |= dep_emp_id.user_id
            if stage.this_employee \
                    and self.employee_id.user_id:
                user_ids |= self.employee_id.user_id
            if stage.user_ids:
                user_ids |= stage.user_ids
            if stage.group_ids:
                for group in stage.group_ids:
                    user_ids |= group.users
        return user_ids

    @api.depends(
        'employee_id',
        'employee_id.parent_id',
        'employee_id.parent_id.user_id',
        'employee_id.department_id',
        'employee_id.department_id.manager_id',
        'employee_id.department_id.manager_id.user_id',
        'next_stage_id',
        'service_type_id',
        'service_type_id.stage_ids',
        'service_type_id.stage_ids.use_domain',
        'service_type_id.stage_ids.domain',
        'service_type_id.stage_ids.group_ids',
        'service_type_id.stage_ids.group_ids.users',
        'service_type_id.stage_ids.user_ids',
        'service_type_id.stage_ids.his_direct_manager',
        'service_type_id.stage_ids.his_department_head',
        'service_type_id.stage_ids.this_employee',
    )
    def _compute_user_ids(self):
        """
        compute users for access right.
        """
        stage_obj = self.with_user(SUPERUSER_ID).env['hr.dynamic.service.stage']
        for rec in self:
            user_ids = self.env['res.users']
            if rec.service_type_id and rec.employee_id:
                stage_data = stage_obj.search(
                    [('service_type_id', '=', rec.service_type_id.id)],
                    order='sequence asc'
                )
                for stage in stage_data:
                    one_stage_user_ids = rec.get_users_from_stage(stage)
                    if not rec.next_stage_id and stage == stage_data[0]:
                        rec.next_stage_user_ids = one_stage_user_ids
                    if rec.next_stage_id and stage == rec.next_stage_id:
                        rec.next_stage_user_ids = one_stage_user_ids
                    if not one_stage_user_ids:
                        msg = "Can't Find Users In Stage: %s " \
                              "In Service Type: %s with Employee: %s" \
                              % (stage.name, rec.service_type_id.name,
                                 rec.employee_id.name)
                        LOGGER.warning(msg)
                    user_ids |= one_stage_user_ids
            rec.user_ids = user_ids

    @api.depends('stage_id', 'stage_id.stage_for_refused')
    def _compute_is_refused(self):
        """
        Compute is refused.
        """
        for rec in self:
            is_refused = False
            if rec.stage_id and rec.stage_id.stage_for_refused:
                is_refused = True
            rec.is_refused = is_refused

    @api.onchange('service_type_id')
    def _onchange_service_type(self):
        """
        Onchange Service Type.
        """
        if self.service_subtype_id.service_type_id != self.service_type_id:
            self.service_subtype_id = False

    def _default_employee(self):
        """
        Get Employee Form User.
        :return: employee <hr.employee>
        """
        return self.env['hr.employee'].search(
            [('user_id', '=', self.env.user.id),
             ('company_id', '=', self.env.company.id)],
            limit=1,
        )

    user_ids = fields.Many2many(
        comodel_name="res.users",
        relation="users_service_rel",
        column1="service_id",
        column2="user_id", string="Users",
        compute=_compute_user_ids,
        store=True,
        compute_sudo=True,
        track_visibility='onchange',
        copy=False,
    )
    next_stage_user_ids = fields.Many2many(
        comodel_name="res.users",
        relation="next_users_service_rel",
        column1="service_id",
        column2="user_id",
        string="Next Approval",
        compute=_compute_user_ids,
        store=True,
        compute_sudo=True,
        track_visibility='onchange',
        copy=False,
    )
    name = fields.Char(
        string="Description", track_visibility='onchange', required=True
    )
    stage = fields.Char(related="stage_id.name", track_visibility='onchange')
    first_stage_action = fields.Char(
        related="first_stage_id.action_name", string="  "
    )
    next_action = fields.Char(related="next_stage_id.action_name", string=" ")
    stage_id = fields.Many2one(comodel_name="hr.dynamic.service.stage",
                               string="Service Stage", copy=False, )
    can_edit = fields.Boolean(related="stage_id.can_edit", store=True)
    can_refuse = fields.Boolean(related="stage_id.can_refuse", store=True)
    is_refused = fields.Boolean(compute=_compute_is_refused, store=True,
                                copy=False)
    refused_by_id = fields.Many2one(
        comodel_name="res.users",
        string="Refused By",
        track_visibility='onchange',
        copy=False,
    )
    refuse_reason = fields.Text(track_visibility='onchange', copy=False)
    next_stage_id = fields.Many2one(
        comodel_name="hr.dynamic.service.stage",
        string="Next Stage",
        compute=_compute_next_stage, store=True,
        copy=False,
    )
    first_stage_id = fields.Many2one(
        comodel_name="hr.dynamic.service.stage",
        string="First Stage",
        compute=_compute_first_stage_id,
        store=True,
        copy=False,
    )
    employee_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Employee",
        required=True,
        track_visibility='onchange',
        default=_default_employee,
    )
    department_id = fields.Many2one(
        comodel_name="hr.department",
        string="Department",
        related="employee_id.department_id",
        track_visibility='onchange'
    )
    service_type_id = fields.Many2one(
        comodel_name="hr.dynamic.service.type",
        track_visibility='onchange',
        string="Service Type",
        required=True,
    )
    service_subtype_id = fields.Many2one(
        comodel_name="hr.dynamic.service.subtype",
        track_visibility='onchange',
        string="Service Subtype",
        required=False,
    )
    is_first_stage = fields.Boolean(string="is First Stage ?", store=True,
                                    compute=_compute_is_first_stage)
    request_date = fields.Datetime(default=fields.Datetime.now, required=True,
                                   track_visibility='onchange', copy=False, )
    notes = fields.Text(track_visibility='onchange', copy=False)
    company_id = fields.Many2one('res.company',
                                 default=lambda rec: rec.env.company.id)
