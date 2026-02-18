""" Integration Test HR Manpower Plan """
from datetime import date
from dateutil.relativedelta import relativedelta

from odoo import SUPERUSER_ID, fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import TransactionCase


class TestHrManpowerPlan(TransactionCase):
    """ Unit Test for test_hr_manpower_plan model """

    def setUp(self):
        """ Setup testing environment """
        super(TestHrManpowerPlan, self).setUp()
        # Setting up manpower users
        self.hr_mngr = self.env.ref('base.user_demo')
        self.hr_mngr.groups_id = [(4, self.env.ref('hr.group_hr_manager').id)]
        self.chairman_user = self.env.ref('base.user_admin')
        self.dep_mngr_usr = self.env['res.users'].sudo().create({
            'name': 'Department Manager',
            'login': True,
            'email': 'dep_mngr@mail.com'
        })
        self.chairman_user.groups_id = [
            (4, self.env.ref('hr_manpower_plan.group_manpower_plan_manager').id)
        ]
        self.dep_management = self.env.ref('hr.dep_management')
        self.dep_mngr_emp = self.env['hr.employee'].sudo().create({
            'name': 'Department Manager',
            'department_id': self.dep_management.id,
            'user_id': self.dep_mngr_usr.id
        })
        self.dep_management.manager_id = self.dep_mngr_emp.id

    # pylint: disable=protected-access,too-many-statements,too-many-locals
    def test_manpower_plan(self):
        """ Test Scenario: creating and managing manpower plan """
        # Creating Manpower Plan
        manpower_plan = self.env['hr.manpower.plan'].with_user(self.hr_mngr)
        plan = manpower_plan.with_user(self.hr_mngr.id).create({
            'date_from': date(date.today().year, 1, 1),
            'date_to': date(date.today().year, 12, 31),
            'deadline': date(date.today().year, 12, 28),
            'department_ids': [(4, self.dep_management.id)],
        })
        # Check that plan fields is not readonly for manager
        self.assertFalse(plan.is_readonly)
        # Check that plan name contains the plan year
        self.assertEqual(
            plan.name, 'PLAN [%s - %s]' % (
                plan.date_from, plan.date_to
            )
        )
        # Test plan sharing
        plan.action_share()
        self.assertTrue(plan.activity_ids)
        activity_user = plan.activity_ids.mapped('user_id').id
        dep_mngr_usr = self.dep_management.manager_id.user_id or \
            SUPERUSER_ID
        self.assertEqual(
            activity_user,
            dep_mngr_usr.id,
            'Activity user is not Department user'
        )
        self.assertEqual(plan.state, 'preparation')
        # add department plans
        plan_line = self.env['hr.manpower.plan.line'].with_user(
            self.dep_mngr_usr
        )
        developer = self.env.ref('hr.job_developer')
        consultant = self.env.ref('hr.job_consultant')
        developer.salary_type = 'fixed'
        developer.salary = 2000
        consultant.salary_type = 'range'
        consultant.max_salary = 5000
        plan_line_1 = plan_line.create({
            'manpower_plan_id': plan.id,
            'job_id': developer.id,
            'planned_no_of_position': 2,
            'reason': 'new_hire',
        })
        plan_line_2 = plan_line.create({
            'manpower_plan_id': plan.id,
            'job_id': consultant.id,
            'planned_no_of_position': 3,
            'reason': 'new_hire',
        })
        plan_line_1.with_user(self.chairman_user.id).approved_no_of_position = 1
        with self.assertRaises(ValidationError):
            plan_line.create({
                'manpower_plan_id': plan.id,
                'job_id': developer.id,
                'planned_no_of_position': 2,
                'reason': 'new_hire',
                'start_date': date(
                    date.today().year, 12, 31) + relativedelta(days=3),
            })
        with self.assertRaises(ValidationError):
            plan_line.create({
                'manpower_plan_id': plan.id,
                'job_id': developer.id,
                'planned_no_of_position': 15,
                'reason': 'replacement',
            })
        # Check that department manager only see their department only
        department_domain = plan_line_1._get_department_domain()
        self.assertEqual(
            department_domain,
            [('manager_id', '=', self.dep_mngr_emp.id)]
        )
        # Check that manager see All department
        department_domain = plan_line_1.with_user(
            self.chairman_user
        )._get_department_domain()
        self.assertEqual(department_domain, [])
        # check that submitting plan line will create activity
        plan_line_1.action_submit()
        self.assertEqual(plan_line_1.state, 'submitted')
        self.assertEqual(
            plan_line_1.with_user(self.chairman_user.id).unit_budget,
            developer.salary
        )
        self.assertTrue(plan_line_1.activity_ids)

        plan_line_2.action_submit()
        self.assertEqual(
            plan_line_2.with_user(self.chairman_user.id).unit_budget,
            consultant.max_salary
        )
        self.assertEqual(plan_line_2.state, 'submitted')
        self.assertTrue(plan_line_2.activity_ids)
        self.assertEqual(
            plan_line_1.activity_ids.mapped('user_id').id,
            self.hr_mngr.id,
            'Activity user is not Department user'
        )
        self.assertEqual(
            plan_line_2.activity_ids.mapped('user_id').id,
            self.hr_mngr.id,
            'Activity user is not Department user'
        )
        # add estimated budget for line 1
        plan_line_1.with_user(self.chairman_user.id).unit_budget = 5000
        # check that budget on replacement will equal the difference between
        # job position range salary and unit budget salary
        plan_line_3 = plan_line.create({
            'manpower_plan_id': plan.id,
            'job_id': consultant.id,
            'planned_no_of_position': 1,
            'reason': 'replacement',
        })
        plan_line_3.action_submit()
        plan_line_3.with_user(self.chairman_user.id).unit_budget = 6000
        plan_line_3.with_user(self.chairman_user.id).action_budget()
        self.assertEqual(plan_line_3.total_budget, 1000)
        plan_line_3.action_approve()
        self.assertEqual(plan_line_3.approved_budget, 1000)

        # check that budget on replacement will equal the difference between
        # job position fixed salary and unit budget salary
        plan_line_4 = plan_line.create({
            'manpower_plan_id': plan.id,
            'job_id': developer.id,
            'planned_no_of_position': 4,
            'reason': 'replacement',
        })
        plan_line_4.action_submit()
        plan_line_4.with_user(self.chairman_user.id).unit_budget = 3000
        plan_line_4.with_user(self.chairman_user.id).action_budget()
        self.assertEqual(plan_line_4.total_budget, 4000)
        plan_line_4.action_approve()
        self.assertEqual(plan_line_4.approved_budget, 4000)

        # Submit plan
        plan.action_submit()
        self.assertEqual(plan.state, 'submitted')
        # Budget plan
        plan_line_1.with_user(self.chairman_user.id).action_budget()
        self.assertEqual(plan_line_1.state, 'budgeted')
        # Reject budget
        plan_line_1.note = 'Over budget'
        plan_line_1.action_reject()
        self.assertEqual(plan_line_1.state, 'rejected')
        # add estimated budget for line 2
        plan_line_2.with_user(self.chairman_user.id).unit_budget = 4000
        # Budget plan
        plan_line_2.with_user(self.chairman_user.id).action_budget()
        self.assertEqual(plan_line_2.state, 'budgeted')
        # Approve budget
        plan_line_2.action_approve()
        self.assertEqual(plan_line_2.state, 'approved')
        # check the budget of the plan
        self.assertEqual(
            plan.planned_budget, sum(
                plan.mapped('manpower_line_ids.total_budget')
            )
        )
        self.assertEqual(
            plan.approved_budget, sum(
                plan.manpower_line_ids.filtered(
                    lambda r: r.state == 'approved'
                ).mapped('approved_budget')
            )
        )
        # View plan lines
        action = plan.action_view_plan_lines()
        self.assertEqual(
            action['domain'],
            [('id', 'in', plan.mapped('manpower_line_ids').ids)]
        )
        # Reject plan
        plan.action_reject()
        self.assertEqual(plan.state, 'rejected')
        # Approve plan
        plan.state = 'submitted'
        plan.action_approve()
        self.assertEqual(plan.state, 'approved')

        # Test start recruitment
        action = plan.action_start_recruitment()
        self.assertEqual(action['context'], {'default_plan_id': plan.id})
        recruitment_replace = self.env['manpower.recruitment'].create(
            {'plan_id': plan.id, 'recruitment_method': 'replace'}
        )
        recruitment_replace.action_start_recruitment()
        self.assertEqual(developer.no_of_recruitment, 4)

        recruitment_add = self.env['manpower.recruitment'].create(
            {'plan_id': plan.id, 'recruitment_method': 'add'}
        )
        recruitment_add.action_start_recruitment()
        self.assertEqual(developer.no_of_recruitment, 8)
        self.assertEqual(plan.state, 'done')
        with self.assertRaises(UserError):
            plan.start_recruitment(method='other')
        # Test that deadline plan will submit
        plan2 = manpower_plan.with_user(self.hr_mngr.id).create({
            'date_from': fields.Date.today() + relativedelta(days=-4),
            'date_to': fields.Date.today() + relativedelta(months=3, days=-3),
            'deadline': fields.Date.today() + relativedelta(days=-1),
            'department_ids': [(4, self.dep_management.id)],
        })
        plan2.action_share()
        plan2.action_deadline_submit()
        self.assertEqual(plan2.state, 'submitted')

        # Test that deadline plan will generate reminder activity
        plan3 = manpower_plan.with_user(self.hr_mngr.id).create({
            'date_from': fields.Date.today(),
            'date_to': fields.Date.today() + relativedelta(months=3, days=-3),
            'deadline': fields.Date.today() + relativedelta(days=3),
            'department_ids': [(4, self.dep_management.id)],
        })
        plan3.action_share()
        plan3.action_deadline_submit()
        self.assertTrue(plan3.activity_ids)
        activity_user = plan3.activity_ids.mapped('user_id').id
        self.assertEqual(
            activity_user,
            dep_mngr_usr.id,
            'Activity user is not Department user'
        )

        manpower_plan_report = self.env[
            "report.hr_manpower_plan.report_manpower_planned"
        ]
        values = manpower_plan_report._get_report_values(plan.id)
        self.assertEqual(values['docs'][0]['manpower'], plan)
        self.assertTrue(plan.sudo().unlink())
