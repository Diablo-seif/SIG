""" init object hr.dynamic.service.stage """

from odoo import _, fields, models
from odoo.exceptions import UserError


class HrDynamicServiceStage(models.Model):
    """ init object hr.dynamic.service.stage """
    _name = 'hr.dynamic.service.stage'
    _rec_name = 'name'
    _description = 'Dynamic Approval Stages'
    _order = 'sequence asc, id asc'

    def _get_default_sequence(self):
        """
        Get next sequence stage.
        :return:
        """
        res = 1
        service_type_id = self.env.context.get('service_type_id', 0)
        service_stage = self.search([
            ('service_type_id', '=', service_type_id)
        ], limit=1, order='sequence desc')
        if service_stage:
            res = service_stage.sequence + 1
        return res

    def unlink(self):
        """
        Prevent refusal stages deletion.
        """
        for record in self:
            if record.stage_for_refused:
                raise UserError(_('You Can Not Delete Refuse Stage.'))
        return super(HrDynamicServiceStage, self).unlink()

    sequence = fields.Integer(default=_get_default_sequence)
    name = fields.Char(required=True, translate=True)
    action_name = fields.Char(required=True)
    can_edit = fields.Boolean(string="Can Edit?", default=False)
    can_refuse = fields.Boolean(string="Can Refuse?", default=False)
    service_type_id = fields.Many2one(
        comodel_name="hr.dynamic.service.type",
        string="Service Type",
    )
    use_domain = fields.Boolean(string="Use Employee Search?")
    domain = fields.Text(string="Employee Domain", default='[]')
    group_ids = fields.Many2many(
        comodel_name="res.groups",
        relation="service_stage_groups_rel",
        column1="stage_id", column2="group_id",
        string="Groups"
    )
    user_ids = fields.Many2many(
        comodel_name="res.users",
        relation="service_stage_user_rel",
        column1="stage_id", column2="user_id",
        string="Users"
    )
    his_direct_manager = fields.Boolean(string="Employee Direct Manager?")
    his_department_head = fields.Boolean(string="Employee Department Head?")
    this_employee = fields.Boolean(string="The Employee?")
    stage_for_refused = fields.Boolean()
    fold = fields.Boolean(string="Folded in kanban view")
    server_action_id = fields.Many2one('ir.actions.server',
                                       string='Related Server Action')
