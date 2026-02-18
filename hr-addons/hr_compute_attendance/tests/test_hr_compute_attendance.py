"""Integrated Tests for hr.compute.attendance and hr.attendance.record"""

from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo.tests.common import TransactionCase


# pylint: disable=no-member
class TestHrComputeAttenance(TransactionCase):
    """Integrated Tests"""

    def setUp(self):
        """Setup the testing environment."""
        super(TestHrComputeAttenance, self).setUp()
        # Useful models
        self.users_obj = self.env['res.users']
        self.compute_obj = self.env['hr.compute.attendance']
        # USERS
        self.attend_manager_user = self.users_obj.create({
            'name': 'Attendance Manager User #1',
            'login': 'attendance_manager@example.com',
            'email': 'attendance_manager@example.com',
            'groups_id': [(6, 0, [self.env.ref('hr_attendance.group_hr'
                                               '_attendance_manager').id,
                                  self.env.ref('hr_contract.'
                                               'group_hr_contract_manager').id,
                                  ])]
        })
        self.calendar_id = self.env['resource.calendar'].sudo().create(
            {"name": "Sample Working Calender#2"}
        )
        self.employee_id = self.env.ref("hr.employee_al")

    def test00_create_compute(self):
        """test Scenario: Create Compute Attendance. """
        start_date = datetime.today().replace(day=1)
        week = start_date.weekday()
        while week not in [4, 5]:
            start_date = start_date + relativedelta(days=1)
            week = start_date.weekday()
        start_date.weekday()
        end_date = start_date + relativedelta(days=30)
        check_in = datetime(start_date.year, start_date.month, start_date.day,
                            12, 45, 00)
        check_out = check_in + relativedelta(minutes=5)
        self.env['hr.attendance'].create({
            'employee_id': self.employee_id.id,
            'check_in': check_in,
            'check_out': check_out,
        })
        context = {'active_ids': [self.employee_id.id],
                   'active_model': "hr.employee", }
        compute_id = self.compute_obj.with_context(**context). \
            with_user(self.attend_manager_user).create(
                {'start_date': start_date, 'end_date': end_date, })
        # pylint: disable=protected-access
        compute_id._onchange_month_year()
        self.assertTrue(compute_id, "attend manager cannot compute record.")
        self.assertTrue(compute_id.employee_ids,
                        "employee_ids must be added by default.")
        self.assertEqual(int(compute_id.month), datetime.now().month,
                         "default month must be equal this month.")
        self.assertEqual(int(compute_id.year), datetime.now().year,
                         "default year must be equal this year.")
        self.assertEqual(compute_id.state, "draft",
                         "default state must be equal `draft`.")
        compute_id.with_user(self.attend_manager_user).action_compute()
        count_lines = compute_id.count_lines
        self.assertTrue(count_lines >= 0,
                        "compute count lines must be large than or equal zero.")
        if count_lines > 0:
            line = compute_id.compute_ids[0]
            line.with_user(self.attend_manager_user).compute_line()
            res_line = line.with_user(self.attend_manager_user).open_line()
            self.assertTrue('search_default_employee_id' in res_line['context'],
                            "context open must be content "
                            "search_default_employee_id.")
            self.assertTrue(line.display_name,
                            "the line must have a display name.")
        res_open = compute_id.with_user(
            self.attend_manager_user).open_compute_lines()
        self.assertTrue(res_open['res_model'] == 'hr.compute.attendance.line',
                        'funtion must be open object '
                        'hr.compute.attendance.line ')
        self.assertEqual(len(compute_id.compute_ids), 1,
                         "compute lines must be added one line.")
        penalties_value = self.employee_id.with_user(
            self.attend_manager_user).get_deduction_penalties()
        self.assertTrue(penalties_value <= 0,
                        "penalties_value must be less than or equal zero.")
