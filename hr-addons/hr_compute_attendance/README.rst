.. class:: text-left

Compute Attendance
==================

Compute Attendance To Create per day record


Features
--------

#. define penalty roles
#. compute attendance to create per day record
#. compute deduction values

Usage
-----

Configuration
~~~~~~~~~~~~~

To configure the attendance computation, from "Attendance" app, select
"Configuration" menu, then enter the following values:

#. Day Start Month: set the HR payroll monthly cycle start day of month.

#. Start Month: set "Day Start Month" to be calculated from "Current" or
   "Previous Month".

#. Midday Time: set to calculate the end time of day for overtime calculations
   of previous day. e.g. an employee checked-in after midnight, this normally
   will be calculated in the new day, but with Midday Time set, it will reflect
   based on the setting.

#. Maximum Penalty Per Day: set maximum penalty value of a single day after
   computing the total penalties. e.g. if total of penalties is 2.00 days, and
   max deduction is 1.00, the rest will be cut off.

#. Absent Interval Deduction Value: set the absent interval value of deduction
   in days. e.g. an employee was absent in an interval with value of 0.5 a day.

#. Compute Missing Hours Based on:

   a. Missing Without Delay In: check it to not calculate lateness as missing
      hours in respective penalty rules (avoid duplicate penatlies).

   b. Missing Without Early Out: check it to not calculate early departure as
      missing hours in respective penalty rules (avoid duplicate penatlies).

Penalty Rules
~~~~~~~~~~~~~~

To configure penalty rules (for lateness, early departure, and missing hours),
from "Attendance" app, select "Configuration" menu, then choose "Penalty
Rules", then create a new one with the following details:

#. Title: name of the rule.

#. Penalty Type: select penalty type from "Late In" for lateness, "Early Out"
   for early departure, and "Missing Hours" for in-between missing hours in
   shifts (work-schedule intervals).

#. Working Schedule: The work-schedule related to this rule. To apply on
   contracts linked to this work schedule only.

#. Delay Minutes From: The start number of minutes that will be matched with
   the rule (for lateness, early departure, or missing hours).

#. Delay Minutes To: The end number of minutes that will be matched with the
   rule (for lateness, early departure, or missing hours).

#. Penalty Rule Values with Redundant: number of occurrences with penalty
   values for each occurrence, with the following details:

   a. Redundant: the order of occurrence.

   b. Penalty Value: the deduction value in days for this occurrence.

Attendance Computation
~~~~~~~~~~~~~~~~~~~~~~

To compute attendance, from "Attendance" app, select "Manage Attendances", then
select "Compute Attendance", then create a new "Compute Attendance" record, and
fill the following fields:

#. Month: Select the attendance computation for a specific month.

#. Year: Select the attendance computation for a specific year.

#. Employees: Select the employees you want to compute their attendance.

Then click "Confirm" to compute the selected employees attendance based on the
month and year selected in the form.

A new line shoud show up for each employee in the list view below the form that
contains the following details:

#. Employee: the employee name.

#. Timezone: the employee timezone.

#. Start Date: the start date of computation.

#. End Date: the end date of computation.

#. Sum Working Schedule Hours: Total number of working hours in the work
   schedule for the computation period.

#. Sum Total Actual Working Hours: Total number of attendance hours in the
   employee's attendance logs.

#. Sum Total Missing Hours: Total number of missing hours when matching the
   work schedule with the employee's attendance logs.

#. Sum Total Penalty Value: Total number of days calculated from penalty rules
   in this computation period (absent intervals not included).

#. Sum Attend Interval: Total number of work-schedule intervals attended by
   this employee based on attendance logs in this computation period.

#. Sum Interval Count: Total number of work schedule intervals for this
   employee in this computation period.

#. Sum Absent Interval: Total number of absent work schedule intervals for this
   employee in this computation period.

#. Sum Absent Penalty Value: Total number of deduction days as penalty of
   absent intervals only.

In each line, there's two buttons to "Re-Compute" the attendance based on later
updates, or "Open" the period computation details of the employee.

Attendance Computation Details
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In the computation details list, you should see the following information:

#. Day: the work-schedule day of attendance (this includes next-day intervals
   if they didn't exceed the "Midday Time" in configuraiton).

#. Date: the day of computation in calendar.

#. Employee: the employee of this computation.

#. Working Schedule Hours: Total number of working hours (of all intervals) of
   this work day.

#. Interval Count: Total number of intervals in this work-schedule day.

#. Total Actual Working Hours: Total number of hours in attendance logs of this
   employee based on the calendar date.

#. Total Missing Hours: Total number of hours missing from attendance logs of
   this employee based on the calendar date.

#. Attend Interval: Total number of work-schedule intervals attended by this
   employee from attendance logs based on the calendar date.

#. Absent Interval: Total number of work-schedule intervals the employee was
   absent in them.

#. Absent Penalty Value: Total number of deduction days on absent intervals
   only.

#. Total Penalty Value: Total number of deduction days on penalty rules only.

When opening a single item of computation details list, you should see the
following information:

#. Day, Date, Employee, Interval Count, Attend Interval, Working Schedule
   Hours, Total Actual Working Hours, Total Missing Hours, Absent Interval,
   Absent Penalty Value, Total Penalty Value: All of these fields are the same
   as the list view.

#. Contract: The selected running contract for this employee at the time of
   computation.

#. Working Schedule: The selected work-schedule on the employee contract at the
   time of computation.

#. Intervals (tab): Under that tab you'll find the following details:

   a. Start Datetime: the start date time for that work-schedule interval.

   b. End Datetime: the end date time for that work-schedule interval.

   c. Working Hours: the total number of hours that should be attended in that
      interval.

   d. Is Attend: a checkbox for the matching between the interval and the
      employee's attendance of that day.

   e. Actual Working Hours: the total number of matched attendance hours for
      this interval.

   f. Delay In: the number of minutes of lateness based on matched attendance
      of that interval.

   g. Penalty In Redundant: the occurrence order of the latness penalty over
      the period of computation.

   h. Penalty In: the matched lateness penalty rule for that interval.

   i. Penalty In Value: the penalty deduction value of lateness in days for
      that interval.

   j. Early Out: the number of minutes of early departure based on matched
      attendance of that interval.

   k. Penalty Out Redundant: the occurrence order of the early departure
      penalty over the period of computation.

   l. Penalty Out: the matched early departure penalty rule for that interval.

   m. Penalty Out Value: the penalty deduction value of the early departure in
      days for that interval.

   n. Missing Hours: total missing hours in that interval.

   o. Penalty Missing Hours: the matched missing hours penalty rule for that
      interval.

   p. Penalty Missing Redundant: the occurrence order of missing hours penalty
      over the period of computation.

   q. Penalty Missing Hours Value: the penalty deduction value of the missing
      hours in days for that interval.

   r. Attendances: the attendance records matched for that interval.

#. Attendances (tab): the matched attendance records of this day.


Salary Rule
-----------

1. Deduction Penalties Percentage python call code:
   result = employee.get_deduction_penalties(payslip.date_from, payslip.date_to, 'percentage')

2. Deduction Penalties Amount python call code:
   result = employee.get_deduction_penalties(payslip.date_from, payslip.date_to, 'amount')

3. Absent Penalties python call code:

    .. code-block:: python

      records = employee.env['hr.attendance.record'].search([('employee_id', '=', employee.id), ('date', '&gt;=', payslip.date_from), ('date', '&lt;=', payslip.date_to), ])
      absent_penalty_value = 0
      for rec in records:
        absent_penalty_value -= rec.absent_penalty_value
      result = absent_penalty_value

4. Deduction Week Penalties python call code:
   result = employee.get_week_deduction_hours(date_form=payslip.date_from, date_to=payslip.date_to)

5. Deduction Month Penalties python call code:
   result = employee.get_month_deduction_hours(date_form=payslip.date_from, date_to=payslip.date_to)


Credits
-------

.. |copy| unicode:: U+000A9 .. COPYRIGHT SIGN
.. |tm| unicode:: U+2122 .. TRADEMARK SIGN

- `Hashem Aly <hashem.aly@core-bpo.com>`_ |copy|
  `CORE B.P.O <http://www.core-bpo.com>`_ |tm| 2020
