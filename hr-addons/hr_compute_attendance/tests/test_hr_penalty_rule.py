"""Integrated Tests for hr.penalty.rule"""

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestHrPenaltyRule(TransactionCase):
    """Integrated Tests"""

    def setUp(self):
        """Setup the testing environment."""
        super(TestHrPenaltyRule, self).setUp()
        # Useful models
        self.users_obj = self.env['res.users']
        self.penalty_obj = self.env['hr.penalty.rule']
        self.redundant_obj = self.env['hr.penalty.redundant']
        # USERS
        self.att_manager_user = self.users_obj.create({
            'name': 'Attendance Manager User #2',
            'login': 'att_manager@example.com',
            'email': 'att_manager@example.com',
            'groups_id': [(6, 0, [self.env.ref('hr_attendance.group_hr'
                                               '_attendance_manager').id])]
        })
        self.calendar_id = self.env['resource.calendar'].create(
            {"name": "Sample Working Calender #4"}
        )

    def test00_create_penalty(self):
        """test Scenario: Create Penalty Rule. """
        penalty_id = self.penalty_obj.with_user(self.att_manager_user).create(
            {'name': 'Sample Penalty Late IN  1M to 15M',
             'calendar_id': self.calendar_id.id,
             'delay_from': 1,
             'delay_to': 15, }
        )
        self.assertTrue(penalty_id, "attend manager cannot create penalty.")
        self.assertTrue(penalty_id.active, "object must be equal True.")
        self.assertEqual(penalty_id.penalty_type, "late_in",
                         "penalty_type must be equal default value `late_in`.")

    def test01create_penalty_redundant(self):
        """test Scenario: Create Penalty Rule with redundant. """
        penalty_id = self.penalty_obj.with_user(self.att_manager_user).create(
            {'name': 'Sample Penalty Late IN  16M to 30M',
             'calendar_id': self.calendar_id.id,
             'delay_from': 16,
             'delay_to': 30, }
        )
        redundant1 = self.redundant_obj.with_user(self.att_manager_user).create(
            {'redundant': 1,
             'penalty_id': penalty_id.id,
             'penalty_value': 0.5, }
        )
        self.assertTrue(redundant1,
                        "attend manager cannot create penalty redundant.")
        self.assertEqual(redundant1.name_get()[0][1], "#1=0.5",
                         "name get must be equal `#1=0.5`.")
        self.redundant_obj.with_user(self.att_manager_user).create(
            {'redundant': 2,
             'penalty_id': penalty_id.id,
             'penalty_value': 1, }
        )
        value_redundant_0 = penalty_id.get_penalty_value_redundant()
        self.assertEqual(value_redundant_0, 0, "value must be equal `0`.")
        value_redundant_1 = penalty_id.get_penalty_value_redundant(redundant=1)
        self.assertEqual(value_redundant_1, 0.5, "value must be equal `0.5`.")
        value_redundant_2 = penalty_id.get_penalty_value_redundant(redundant=2)
        self.assertEqual(value_redundant_2, 1, "value must be equal `1`.")
        value_redundant_3 = penalty_id.get_penalty_value_redundant(redundant=3)
        self.assertEqual(value_redundant_3, 1,
                         "value 3 or more must be equal `1`.")
        penalty_type_str = dict(
            self.penalty_obj.fields_get(allfields=['penalty_type'])[
                'penalty_type']['selection'])["late_in"]
        msg = "You Cannot have 2 Penalty Rules that have " \
              "Overlaps on Minutes With Work schedule: %s " \
              "and Penalty Type: %s" % (self.calendar_id.name, penalty_type_str)
        with self.assertRaisesRegex(UserError, msg,
                                    msg="constraints must be raise exception "
                                        "overlap penalty."):
            self.penalty_obj.with_user(self.att_manager_user).create(
                {'name': 'Sample Penalty Late IN  30M to 35M',
                 'calendar_id': self.calendar_id.id,
                 'delay_from': 20,
                 'delay_to': 35, }
            )
