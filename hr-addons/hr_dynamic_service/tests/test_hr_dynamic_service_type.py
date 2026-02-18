"""Integrated Tests for hr_dynamic_service_type"""

from odoo.tests.common import TransactionCase


# pylint: disable=too-many-instance-attributes
class TestHrDynamicServiceType(TransactionCase):
    """Integrated Tests"""

    # pylint: disable=invalid-name
    def setUp(self):
        """Setup the testing environment."""
        super(TestHrDynamicServiceType, self).setUp()
        # Useful models
        self.ResUsers = self.env['res.users']
        self.HrEmployee = self.env['hr.employee']
        self.HrDynamicServiceType = self.env['hr.dynamic.service.type']
        self.HrDynamicServiceStage = self.env['hr.dynamic.service.stage']
        self.HrDynamicServiceSubtype = self.env['hr.dynamic.service.subtype']

        # Groups
        self.group_hr_manager = self.env.ref('hr.group_hr_manager').id

        # USERS
        user_manage_ds_type_value = {
            'name': 'Sample User Manage Dynamic Approval Type',
            'login': 'manage_service_type@example.com',
            'email': 'manage_service_type@example.com',
            'groups_id': [(6, 0, [self.group_hr_manager])]
        }
        self.user_manage_ds_type = self.ResUsers.with_context(
            **{'no_reset_password': True}).create(user_manage_ds_type_value)

    def test_00_create_service_type(self):
        """ test Scenario: Create Dynamic Approval Type
         with stages and subtypes """
        stages = self.HrDynamicServiceStage.create({
            'sequence': 1,
            'name': 'Stage #1 Draft',
            'action_name': 'Set To Draft',
            'his_direct_manager': True,
            'his_department_head': True,
            'this_employee': True,
        })
        stages |= self.HrDynamicServiceStage.create({
            'sequence': 2,
            'name': 'Stage #2 Confirmed',
            'action_name': 'Confirm',
            'his_direct_manager': True,
            'his_department_head': True,
            'this_employee': True,
        })
        stages |= self.HrDynamicServiceStage.create({
            'name': 'Stage #3 Approved',
            'action_name': 'Approve',
            'his_direct_manager': True,
            'his_department_head': True,
            'this_employee': True,
        })

        subtypes = self.HrDynamicServiceSubtype.create({
            'name': "Subtype #1",
            'sequence': 1,
        })
        subtypes |= self.HrDynamicServiceSubtype.create({
            'name': "Subtype #2",
            'sequence': 2,
        })
        subtypes |= self.HrDynamicServiceSubtype.create({
            'name': "Subtype #3",
            'sequence': 3,
        })

        subtypes |= self.HrDynamicServiceSubtype.create({
            'name': "Subtype #4",
        })

        service_type_values = {
            'sequence': 10,
            'name': "Dynamic Approval Type #1",
            'icon': "fa fa-heart",
            'stage_ids': [(6, 0, stages.ids)],
            'subtype_ids': [(6, 0, subtypes.ids)],
        }
        service_type = self.HrDynamicServiceType. \
            with_user(self.user_manage_ds_type).create(service_type_values)
        self.assertTrue(service_type, "test create service type done.")
        self.assertTrue(service_type.refuse_stage_id,
                        "test auto create stage refuse done.")
        service_type_values_2 = {
            'name': "Dynamic Approval Type #2",
            'icon': "fa fa-heart",
            'stage_ids': [(6, 0, stages.ids)],
            'subtype_ids': [(6, 0, subtypes.ids)],
        }
        service_type_2 = self.HrDynamicServiceType. \
            with_user(self.user_manage_ds_type).create(service_type_values_2)
        self.assertEqual(service_type_2.sequence, 11,
                         "test default sequence service type done.")
        res = subtypes[0].action_open_draft_requests()
        self.assertTrue(res['context'].get('search_default_request_draft'))
        res = subtypes[0].action_open_progress_requests()
        self.assertTrue(res['context'].get('search_default_request_progress'))
        res = subtypes[0].action_open_done_requests()
        stages[1].unlink()
        self.assertTrue(res['context'].get('search_default_request_done'))
