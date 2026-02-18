""" init object hr.dynamic.service.type """

from odoo import _, api, fields, models


class HrServiceDynamicType(models.Model):
    """ init object hr.dynamic.service.type"""
    _name = 'hr.dynamic.service.type'
    _rec_name = 'name'
    _description = 'Dynamic Approval Type'
    _order = 'sequence asc, id asc'
    _inherit = ['mail.thread']

    def _get_default_sequence(self):
        """
        Get next sequence type.
        :return:
        """
        res = 1
        service_type = self.search([], limit=1, order='sequence desc')
        if service_type:
            res = service_type.sequence + 1
        return res

    # pylint: disable=no-member
    @api.model
    def create(self, vals_list):
        """
        Override create function to add stage for refuse.
        :param vals:
        :return:
        """
        res = super(HrServiceDynamicType, self).create(vals_list)
        if not res.refuse_stage_id:
            stage_obj = self.env['hr.dynamic.service.stage']
            group = self.env.ref("hr.group_hr_manager")
            stage_values = {
                'sequence': 0,
                'name': _("Refuse"),
                'action_name': _("Refuse"),
                'stage_for_refused': True,
                'service_type_id': res.id,
                'his_direct_manager': True,
                'his_department_head': True,
                'group_ids': [(6, 0, [group.id])],
            }
            res.refuse_stage_id = stage_obj.create(stage_values).id
        return res

    sequence = fields.Integer(default=_get_default_sequence)
    name = fields.Char(required=True, translate=True)
    icon = fields.Char(required=True)
    stage_ids = fields.One2many(
        comodel_name="hr.dynamic.service.stage",
        inverse_name="service_type_id",
        string="Status", required=True
    )
    subtype_ids = fields.One2many(
        comodel_name="hr.dynamic.service.subtype",
        inverse_name="service_type_id",
        string="Subtypes", required=True
    )
    refuse_stage_id = fields.Many2one(comodel_name="hr.dynamic.service.stage")
    delete_in_first_stage = fields.Boolean(
        string="Able to Delete The Request in First Stage?",
        default=True
    )
    company_id = fields.Many2one('res.company',
                                 default=lambda rec: rec.env.company.id)
