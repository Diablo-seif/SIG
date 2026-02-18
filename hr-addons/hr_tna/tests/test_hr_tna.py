""" Integration Test HR Manpower Plan """
from datetime import date
from dateutil.relativedelta import relativedelta

from odoo import SUPERUSER_ID, fields
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestHrTna(TransactionCase):
    """ Unit Test for test_hr_tna model """

    def setUp(self):
        """ Setup testing environment """
        super().setUp()
        # Setting up TNA users
        self.hr_mngr = self.env.ref('base.user_demo')
        self.dep_management = self.env.ref('hr.dep_management')
        self.hr_mngr.groups_id = [
            (4, self.env.ref('hr.group_hr_manager').id),
            (4, self.env.ref('hr_tna.group_tna_budget').id)
        ]
        self.chairman_user = self.env.ref('base.user_admin')
        self.chairman_user.groups_id = [
            (4, self.env.ref('hr_tna.group_tna_manager').id)
        ]
        self.dep_mngr_usr = self.env['res.users'].sudo().create({
            'name': 'Department Manager',
            'login': True,
            'email': 'dep_mngr@mail.com',
            'groups_id': [
                (4, self.env.ref('hr_tna.group_tna_user').id),
                (4, self.env.ref('base.group_user').id)
            ]
        })
        self.dep_mngr_emp = self.env['hr.employee'].sudo().create({
            'name': 'Department Manager',
            'department_id': self.dep_management.id,
            'user_id': self.dep_mngr_usr.id
        })
        self.dep_management.manager_id = self.dep_mngr_emp.id

    # pylint: disable=protected-access,too-many-statements,too-many-locals
    def test_tna(self):
        """ Test Scenario: creating and managing TNA """
        # Creating TNA
        tna = self.env['hr.tna'].with_user(self.hr_mngr)
        tna_line = self.env['hr.tna.line'].with_user(self.dep_mngr_usr)
        tna_plan = tna.with_user(self.hr_mngr.id).create({
            'date_from': date(date.today().year, 1, 1),
            'date_to': date(date.today().year, 12, 31),
            'deadline': date(date.today().year, 12, 28),
            'department_ids': [(4, self.dep_management.id)],
        })
        # Check that TNA fields is not readonly for manager
        self.assertFalse(tna_plan.is_readonly)
        # Check that TNA name contains the plan year
        self.assertEqual(tna_plan.name, 'TNA [%s - %s]' % (
            tna_plan.date_from, tna_plan.date_to
        ))
        # Test plan sharing
        tna_plan.action_share()
        self.assertTrue(tna_plan.activity_ids)
        activity_user = tna_plan.activity_ids.mapped('user_id').id
        dep_mngr_usr = self.dep_management.manager_id.user_id or SUPERUSER_ID
        self.assertEqual(activity_user, dep_mngr_usr.id)
        self.assertEqual(tna_plan.state, 'preparation')
        # add department plans
        course1 = self.env.ref('hr_courses.course_1')
        job1 = self.env.ref('hr.job_ceo')
        job2 = self.env.ref('hr.job_cto')
        job3 = self.env.ref('hr.job_consultant')
        provider2 = self.env.ref('hr_courses.provider_1')
        tna_line_1 = tna_line.create({
            'tna_id': tna_plan.id,
            'job_id': job1.id,
            'no_of_participants': 1,
            'course_id': course1.id,
        })
        with self.assertRaises(ValidationError):
            tna_line.create({
                'tna_id': tna_plan.id,
                'job_id': job2.id,
                'no_of_participants': 5,
                'course_id': course1.id,
            })
        # Check that department manager only see their department only
        department_domain = tna_line_1._get_department_domain()
        self.assertEqual(
            department_domain,
            [('manager_id', '=', self.dep_mngr_emp.id)]
        )
        # Check that manager see All department
        department_domain = tna_line_1.with_user(
            self.chairman_user)._get_department_domain()
        self.assertEqual(department_domain, [])
        # check that submitting plan line will create activity
        tna_line_1.action_submit()
        # check that open_form button opens the right record
        self.assertEqual(tna_line_1.open_form()['res_id'], tna_line_1.id)

        tna_line_1.action_submit()
        self.assertEqual(tna_line_1.state, 'submitted')
        set_provider = self.env['hr.tna.set.provider'].with_context(**{
            'active_model': 'hr.tna.line',
            'active_ids': tna_line_1.ids,
        }).create({})
        # Test set provider Wizard
        self.assertTrue(set_provider.course_provider_lines_ids)
        set_provider.course_provider_lines_ids.provider_id = provider2.id
        with self.assertRaises(ValidationError):
            tna_line.create({
                'tna_id': tna_plan.id,
                'job_id': job3.id,
                'no_of_participants': 15,
                'course_id': course1.id,
            })
        set_provider.set_provider()
        self.assertTrue(tna_line_1.provider_id, provider2)
        min_cost = provider2.cost_per_participant * \
            provider2.minimum_no_of_participants
        self.assertEqual(
            tna_line_1.with_user(self.chairman_user.id).unit_budget,
            min_cost
        )
        self.assertTrue(tna_line_1.activity_ids)
        self.assertEqual(
            tna_line_1.activity_ids.mapped('user_id').id, self.hr_mngr.id
        )
        # Submit plan
        tna_plan.action_submit()
        self.assertEqual(tna_plan.state, 'submitted')
        # Budget plan
        tna_line_1.with_user(self.chairman_user.id).action_budget()
        self.assertEqual(tna_line_1.state, 'budgeted')
        # Reject budget
        tna_line_1.note = 'Over budget'
        tna_line_1.with_user(self.chairman_user.id).action_reject()
        self.assertEqual(tna_line_1.state, 'rejected')
        tna_line_1.state = 'budgeted'
        # Approve budget
        tna_line_1.with_user(self.chairman_user.id).action_approve()
        self.assertEqual(tna_line_1.state, 'approved')
        emp1 = self.env.ref('hr.employee_admin')
        emp2 = self.env.ref('hr.employee_qdp')
        with self.assertRaises(ValidationError):
            tna_line_1.tna_course_ids = [
                (0, 0, {
                    'employee_id': emp1.id,
                    'estimated_date': fields.Date.today()
                }),
                (0, 0, {
                    'employee_id': emp2.id,
                    'estimated_date': fields.Date.today()
                }),
            ]
        with self.assertRaises(ValidationError):
            tna_line_1.tna_course_ids = [(0, 0, {
                'employee_id': emp2.id,
                'estimated_date': date(date.today().year+1, 1, 5)
            })]
        self.env.ref('hr_tna.tna_courses_sequence').number_next_actual = 1
        course_line = self.env['hr.tna.courses'].create({
            'tna_line_id': tna_line_1.id,
            'employee_id': emp2.id,
            'estimated_date': fields.Date.today()
        })
        # check total number of courses for employee
        self.assertEqual(
            emp2.course_count,
            len(emp2.mapped('planned_course_ids'))
        )
        self.assertEqual(
            emp2.action_view_course()['domain'],
            [('id', 'in', emp2.mapped('planned_course_ids').ids)]
        )
        self.assertEqual(course_line.name, 'COURSE/00001')
        # check the budget of the plan
        self.assertEqual(
            tna_plan.planned_budget,
            sum(tna_plan.tna_line_ids.mapped('planned_budget'))
        )
        self.assertEqual(
            tna_plan.approved_budget,
            sum(tna_plan.tna_line_ids.filtered(
                lambda r: r.state == 'approved').mapped('approved_budget'))
        )
        self.assertEqual(
            tna_plan.internal_budget,
            sum(tna_plan.tna_line_ids.filtered(
                lambda r: r.provider_type == 'internal'
            ).mapped('approved_budget'))
        )
        self.assertEqual(
            tna_plan.external_budget,
            sum(tna_plan.tna_line_ids.filtered(
                lambda r: r.provider_type == 'external'
            ).mapped('approved_budget'))
        )
        # View plan lines
        action = tna_plan.action_view_tna_lines()
        self.assertEqual(
            action['domain'],
            [('id', 'in', tna_plan.mapped('tna_line_ids').ids)]
        )

        # Reject plan
        tna_plan.with_user(self.chairman_user).action_reject()
        self.assertEqual(tna_plan.state, 'rejected')
        # Approve plan
        tna_plan.state = 'submitted'
        tna_plan.with_user(self.chairman_user).action_approve()
        self.assertEqual(tna_plan.state, 'approved')

        tna_plan2 = tna.with_user(self.hr_mngr.id).create({
            'date_from': fields.Date.today() + relativedelta(days=-4),
            'date_to': fields.Date.today() + relativedelta(months=3, days=-3),
            'deadline': fields.Date.today() + relativedelta(days=-1),
            'department_ids': [(4, self.dep_management.id)],
        })
        tna_plan2.with_user(self.chairman_user).action_share()
        tna_plan2.action_deadline_submit()
        self.assertEqual(tna_plan2.state, 'submitted')

        # Test that deadline plan will generate reminder activity
        tna_plan3 = tna.with_user(self.hr_mngr.id).create({
            'date_from': fields.Date.today(),
            'date_to': fields.Date.today() + relativedelta(months=3, days=-3),
            'deadline': fields.Date.today() + relativedelta(days=3),
            'department_ids': [(4, self.dep_management.id)],
        })
        tna_plan3.with_user(self.chairman_user).action_share()
        tna_plan3.action_deadline_submit()
        self.assertTrue(tna_plan3.activity_ids)
        activity_user = tna_plan3.activity_ids.mapped('user_id').id
        self.assertEqual(
            activity_user,
            dep_mngr_usr.id,
        )

        tna_report = self.env[
            "report.hr_tna.tna_report"
        ]
        values = tna_report._get_report_values(tna_plan.id)
        self.assertEqual(values['docs'][0]['tna'], tna_plan)
        self.assertTrue(tna_plan3.sudo().unlink())
