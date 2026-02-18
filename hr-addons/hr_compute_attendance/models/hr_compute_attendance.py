""" init object hr_compute_attendance"""

from datetime import date

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError

MONTH_SELECTION = [('01', 'January'), ('02', 'February'), ('03', 'March'),
                   ('04', 'April'), ('05', 'May'), ('06', 'June'),
                   ('07', 'July'), ('08', 'August'), ('09', 'September'),
                   ('10', 'October'), ('11', 'November'), ('12', 'December')]


# pylint: disable=no-member
class HrComputeAttendance(models.Model):
    """ init object hr_compute_attendance"""
    _name = 'hr.compute.attendance'
    _inherit = ['mail.thread']
    _description = 'Compute Attendance'

    def action_compute(self, compute_direct=True):
        """
        Action Compute.
        """
        self.ensure_one()
        if self.compute_ids:
            self.compute_ids.unlink()
        employee_ids = self.env['hr.employee']
        if self.employee_ids:
            employee_ids |= self.employee_ids
        if self.department_ids:
            dep_employee_ids = self.env['hr.employee'].search(
                [('department_id', 'in', self.department_ids.ids)])
            employee_ids |= dep_employee_ids
        if not employee_ids:
            employee_ids = self.env['hr.employee'].search([])
        for emp in employee_ids:
            self.env['hr.compute.attendance.line'].create({
                'compute_id': self.id,
                'employee_id': emp.id,
                'start_date': self.start_date,
                'end_date': self.end_date,
            })
        if self.compute_ids and compute_direct:
            self.compute_ids.compute_line()

    def unlink(self):
        """
        Override unlink to raise if not draft.
        """
        for record in self:
            if record.state != 'draft':
                raise UserError(_("You Can Delete Only in Draft Status."))
        return super(HrComputeAttendance, self).unlink()

    # pylint: disable=no-self-use
    def _default_month(self):
        """
        Get Current Month.
        :return: Current Month <string>
        """
        month = date.today().month
        if month < 10:
            return '0' + str(month)
        return str(month)

    # pylint: disable=no-self-use
    def _get_month_selection(self):
        """
        Get List Of Month Selection.
        :return: list of Month <tuples>
        """
        return MONTH_SELECTION

    # pylint: disable=no-self-use
    def _get_year_selection(self):
        """
        Get List Of Year Selection.
        :return: list of Year <tuples>
        """
        year = date.today().year - 50
        years = []
        # pylint: disable=unused-variable
        for step in range(100):
            years.append((str(year), str(year)))
            year += 1
        return years

    # pylint: disable=no-self-use
    def _default_year(self):
        """
        Get Current Year.
        :return: Current Year <string>
        """
        return str(date.today().year)

    def _get_default_employees(self):
        """
        Get Default Employee List if send on context.
        :return:
        """
        employee_ids = self.env['hr.employee']
        ctx = self.env.context
        if 'active_ids' in ctx and 'active_model' in ctx \
                and ctx.get('active_model') == "hr.employee":
            employee_ids = self.env['hr.employee'].browse(ctx.get('active_ids'))
        return employee_ids

    @api.model
    def create(self, vals_list):
        """
        Override create to add sequence.
        :param values:
        """
        vals_list['name'] = self.env['ir.sequence'].next_by_code(
            'hr.compute.attendance') or ' '
        return super(HrComputeAttendance, self).create(vals_list)

    @api.depends('compute_ids')
    def _compute_count_lines(self):
        """
        Compute Count Lines
        """
        for rec in self:
            count_lines = 0
            if rec.compute_ids:
                count_lines = len(rec.compute_ids)
            rec.count_lines = count_lines

    def open_compute_lines(self):
        """
        Open Compute Lines
        """
        self.ensure_one()
        context = self.env.context.copy()
        if not self.compute_ids:
            return {}
        return {
            'name': _('Compute Lines'),
            'view_type': 'form',
            'view_mode': 'list,form',
            'res_model': 'hr.compute.attendance.line',
            'views': [(self.env.ref('hr_compute_attendance.view_hr_compute'
                                    '_attendance_line_tree').id, 'lsit'),
                      (self.env.ref('hr_compute_attendance.view_hr_compute'
                                    '_attendance_line_form').id, 'form')],
            'context': context,
            'type': 'ir.actions.act_window',
            'domain': [('id', '=', self.compute_ids.ids)],
        }

    @api.onchange('month', 'year')
    def _onchange_month_year(self):
        """
        Onchange Month Or year Compute Start and end Dates.
        """
        if self.month and self.year:
            conf_sudo = self.env['ir.config_parameter'].sudo()
            day_start_month_str = conf_sudo.get_param('day_start_month',
                                                      default="1")
            start_month_str = conf_sudo.get_param('start_month',
                                                  default="current")
            day_start_month = int(day_start_month_str) or 1
            months = 0
            if start_month_str == 'previous':
                months = -1
            s_date = date(int(self.year), int(self.month), day_start_month)
            start_date = s_date + relativedelta(months=months)
            end_date = start_date + relativedelta(months=1, days=-1)
            self.start_date = start_date
            self.end_date = end_date

    name = fields.Char(string="Sequence")
    description = fields.Text()
    employee_ids = fields.Many2many(comodel_name="hr.employee",
                                    relation="compute_employee_rel",
                                    column1="compute_id",
                                    column2="employee_id",
                                    string="Employees",
                                    default=_get_default_employees)
    department_ids = fields.Many2many(comodel_name="hr.department",
                                      relation="compute_department_rel",
                                      column1="compute_id",
                                      column2="department_id",
                                      string="Departments")
    month = fields.Selection(default=_default_month, required=True,
                             selection=_get_month_selection)
    year = fields.Selection(default=_default_year, required=True,
                            selection=_get_year_selection)
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    state = fields.Selection(string="Status", default="draft",
                             selection=[('draft', 'Draft'),
                                        ('in_progress',
                                         'In Progress'),
                                        ('done', 'Done')])
    compute_ids = fields.One2many(
        comodel_name="hr.compute.attendance.line",
        inverse_name="compute_id",
        string="Compute Lines")
    count_lines = fields.Integer(compute=_compute_count_lines,
                                 store=True)
    company_id = fields.Many2one('res.company',
                                 default=lambda rec: rec.env.company.id)
