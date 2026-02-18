"""Integrated Tests for hr_dynamic_service"""

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase
from odoo.tools.translate import _


# pylint: disable=too-many-instance-attributes
class TestHrDynamicService(TransactionCase):
    """Integrated Tests"""

    # pylint: disable=invalid-name
    def setUp(self):
        """Setup the testing environment."""
        super(TestHrDynamicService, self).setUp()
        # Useful models
        self.ResUsers = self.env['res.users']
        self.HrDynamicServiceRefuse = self.env['hr.dynamic.service.refuse']
        self.HrEmployee = self.env['hr.employee']
        self.HrDepartment = self.env['hr.department']
        self.HrDynamicService = self.env['hr.dynamic.service']
        self.HrDynamicServiceType = self.env['hr.dynamic.service.type']
        self.HrDynamicServiceStage = self.env['hr.dynamic.service.stage']
        self.HrDynamicServiceSubtype = self.env['hr.dynamic.service.subtype']
        # USERS
        self.user_hr = self.ResUsers.create(
            {
                'name': 'Sample User Manage Dynamic Approval Type',
                'login': 'manage_service_type@example.com',
                'email': 'manage_service_type@example.com',
                'groups_id': [(6, 0, [self.env.ref(
                    'hr.group_hr_user'
                ).id, self.env.ref('hr.group_hr_user').id])]
            })
        self.user_employee = self.ResUsers.create(
            {
                'name': 'Sample Employee',
                'login': 'emoloyee@example.com',
                'email': 'emoloyee@example.com',
                'groups_id': [
                    (6, 0, [self.env.ref('base.group_user').id])]
            })
        self.user_other_employee = self.ResUsers.create(
            {
                'name': 'Sample Other Employee',
                'login': 'other_emoloyee@example.com',
                'email': 'other_emoloyee@example.com',
                'groups_id': [
                    (6, 0, [self.env.ref('base.group_user').id])]
            })

        self.user_employee_manager = self.ResUsers.create(
            {
                'name': 'Sample Employee Manager',
                'login': 'emoloyee_manager@example.com',
                'email': 'emoloyee_manager@example.com',
                'groups_id': [
                    (6, 0, [self.env.ref(
                        'hr.group_hr_user'
                    ).id])]
            })

        self.user_employee_department = self.ResUsers.create({
            'name': 'Sample Employee Head Department',
            'login': 'emoloyee_department@example.com',
            'email': 'emoloyee_department@example.com',
            'groups_id': [
                (6, 0, [self.env.ref('base.group_user').id])]
        })
        # Department
        self.department = self.HrDepartment.create({'name': 'SampleDepartment'})
        # Employees
        self.employee_manager = self.HrEmployee.create({
            'name': 'Sample Employee Manager',
            'department_id': self.department.id,
            'user_id': self.user_employee_manager.id,
        })

        self.employee_department = self.HrEmployee.create({
            'name': 'Smaple Employee Head Department',
            'department_id': self.department.id,
            'user_id': self.user_employee_department.id,
        })

        self.employee = self.HrEmployee.create({
            'name': 'Sample Employee',
            'department_id': self.department.id,
            'user_id': self.user_employee.id,
            'parent_id': self.employee_manager.id,
        })

        self.other_employee = self.HrEmployee.create({
            'name': 'Sample Other Employee',
            'department_id': self.department.id,
            'user_id': self.user_other_employee.id,
            'parent_id': self.employee_manager.id,
        })

        # Update Department Manager
        self.department.write({'manager_id': self.employee_department.id})

        # Service Types
        self.service_type_id = self.HrDynamicServiceType.create({
            'name': "Dynamic Approval Type #1",
            'icon': "fa fa-heart",
        })
        # Service Subtypes
        self.subtype_ids = self.HrDynamicServiceSubtype.create({
            'name': "Subtype #1",
            'sequence': 1,
            'service_type_id': self.service_type_id.id,
        })
        self.subtype_ids |= self.HrDynamicServiceSubtype.create({
            'name': "Subtype #2",
            'sequence': 2,
            'service_type_id': self.service_type_id.id,
        })
        self.subtype_ids |= self.HrDynamicServiceSubtype.create({
            'name': "Subtype #3",
            'sequence': 3,
            'service_type_id': self.service_type_id.id,
        })
        self.subtype_ids |= self.HrDynamicServiceSubtype.create({
            'name': "Subtype #4",
            'sequence': 4,
            'service_type_id': self.service_type_id.id,
        })
        # Service Stages
        self.stage_ids = self.HrDynamicServiceStage.create({
            'sequence': 1,
            'name': 'Stage #1 Draft',
            'action_name': 'Set To Draft',
            'can_edit': True,
            'this_employee': True,
            'use_domain': True,
            'domain': [["active", "=", True]],
            'service_type_id': self.service_type_id.id,
        })
        self.stage_ids |= self.HrDynamicServiceStage.create({
            'sequence': 2,
            'name': 'Stage #2 Confirmed',
            'action_name': 'Confirm',
            'can_refuse': True,
            'this_employee': True,
            'service_type_id': self.service_type_id.id,
        })
        self.stage_ids |= self.HrDynamicServiceStage.create({
            'sequence': 2,
            'name': 'Stage #3 Approved',
            'action_name': 'Approve',
            'can_refuse': True,
            'his_direct_manager': True,
            'his_department_head': True,
            'service_type_id': self.service_type_id.id,
        })
        self.stage_ids |= self.HrDynamicServiceStage.create({
            'sequence': 2,
            'name': 'Stage #4 Done',
            'action_name': 'Done',
            'can_refuse': True,
            'group_ids': [(6, 0, [self.env.ref("hr.group_hr_manager").id])],
            'service_type_id': self.service_type_id.id,
        })

    def _create_dynamic_service(self, values=None, user=None):
        """
        Helper function to create Dynamic Approval.
        :param values: dict
        :param user: user to create
        :return: object hr.dynamic.service
        """
        if not values:
            values = {
                'name': "Sample Dynamic Approval Request #1",
                'employee_id': self.employee.id,
                'service_type_id': self.service_type_id.id,
                'service_subtype_id': self.subtype_ids[0].id,
            }
        if not user:
            user = self.user_hr
        return self.HrDynamicService.with_user(user).create(values)

    def test_00_create_dynamic_service(self):
        """test Scenario: Create Dynamic Approval Request"""
        request = self._create_dynamic_service()
        self.assertTrue(request, "test create service request.")

    def test_01_next_action_dynamic_service(self):
        """test Scenario: Next Action Dynamic Approval Request"""
        request = self._create_dynamic_service()
        self.assertTrue(request.first_stage_id,
                        "test request have first state.")
        next_stage = request.next_stage_id
        request.with_user(self.user_hr).run_next_action()
        self.assertEqual(request.stage_id, next_stage,
                         "test action next stage request.")
        self.assertEqual(self.stage_ids[1].id, request.stage_id.id,
                         "test Stage Now Is #2.")
        self.assertEqual(self.stage_ids[2].id, request.next_stage_id.id,
                         "test Next Stage Is #3.")
        request.with_user(self.user_hr).run_next_action()
        self.assertEqual(self.stage_ids[3].id, request.next_stage_id.id,
                         "test Next Stage Is #4.")
        # test unlink
        error_massage = _('You Cannot Delete this Request.')
        with self.assertRaisesRegex(UserError, error_massage):
            request.with_user(self.user_employee_manager).unlink()
        request.action_first_stage()
        self.assertTrue(request.is_first_stage)
        self.assertTrue(request.name)
        request.unlink()

    def test_02_refuse_dynamic_service(self):
        """test Scenario: Refuse Dynamic Approval Request"""
        request = self._create_dynamic_service()
        first_stage = request.stage_id
        refuse_stage = request.service_type_id.refuse_stage_id
        request.with_user(self.user_hr).run_next_action()
        self.assertTrue(request.stage_id.can_refuse,
                        "test now can refuse.")
        refuse_reason = 'Sample Refuse Reason.'
        context = {
            'active_ids': [request.id],
            'active_model': 'hr.dynamic.service'
        }
        service_refuse = self.HrDynamicServiceRefuse.with_user(
            self.user_hr).with_context(**context).create({
                'refuse_reason': refuse_reason
            })
        service_refuse.with_context(
            **context).action_refuse()
        self.assertEqual(request.stage_id, refuse_stage,
                         "test action refuse request.")
        self.assertTrue(request.is_refused,
                        "test request marked as is refused.")
        self.assertEqual(request.refuse_reason, refuse_reason,
                         "test request have the reason.")
        request.with_user(self.user_hr).set_first_stage()
        self.assertEqual(request.stage_id, first_stage,
                         "test action reset first stage request.")
        error_massage = _('Error! You Cannot Refuse this Stage.')
        self.assertFalse(request.stage_id.can_refuse,
                         "test now cannot refuse.")
        with self.assertRaisesRegex(UserError, error_massage):
            self.HrDynamicServiceRefuse.with_user(
                self.user_employee_manager
            ).with_context(**context).create({
                'refuse_reason': refuse_reason
            }).with_context(**context).action_refuse()

    def test_03_invited_only_see_requests(self):
        """test Scenario: Invited Only See Dynamic Approval Requests"""
        self._create_dynamic_service()
        other_requests = self.HrDynamicService. \
            with_user(self.user_other_employee).search([])
        self.assertFalse(other_requests,
                         "test not invited cannot see requests")
