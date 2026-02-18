""" init object dynamic.service.refuse"""

import logging

from odoo import _, fields, models, SUPERUSER_ID
from odoo.exceptions import UserError

LOGGER = logging.getLogger(__name__)


class HrDynamicRefues(models.TransientModel):
    """ init object dynamic.service.refuse"""
    _name = 'hr.dynamic.service.refuse'
    _description = 'Wizard Dynamic Approval Refuse'

    # pylint: disable=inconsistent-return-statements
    def action_refuse(self):
        """
        Action marker Dynamic Approval as is_refused with reason.
        """
        self.ensure_one()
        context = self.env.context
        service_obj = self.env['hr.dynamic.service']
        if self.refuse_reason \
                and 'active_model' in context \
                and 'active_ids' in context \
                and context.get('active_model', False) == 'hr.dynamic.service' \
                and context.get('active_ids', []):
            dynamic_services = service_obj.browse(context.get('active_ids', []))
            for dynamic_service in dynamic_services:
                if not dynamic_service.can_refuse:
                    raise UserError(_('Error! You Cannot Refuse this Stage.'))
                if not dynamic_service.service_type_id.refuse_stage_id:
                    raise UserError(_('Error! No Refuse Stage.'))
                refused_users = dynamic_service.get_users_from_stage(
                    dynamic_service.service_type_id.refuse_stage_id
                )
                refused_users |= self.env.ref("hr.group_hr_user").with_user(
                    SUPERUSER_ID).users
                if self.env.user not in refused_users:
                    raise UserError(_('Error! You do not have '
                                      'a permission to refused this request.'))
                if dynamic_service.service_type_id \
                        and dynamic_service.service_type_id.refuse_stage_id:
                    dynamic_service.stage_id = dynamic_service. \
                        service_type_id.refuse_stage_id.id
                    dynamic_service.refuse_reason = self.refuse_reason
                    dynamic_service.refused_by_id = self.env.user.id
                    return dynamic_service.run_server_action(
                        dynamic_service.service_type_id.refuse_stage_id
                    )

    refuse_reason = fields.Text(required=True)
