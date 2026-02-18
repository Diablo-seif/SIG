""" HR Employee model """

from collections import OrderedDict, defaultdict

from odoo import api, fields, models


# pylint: disable=no-member
class HrEmployee(models.Model):
    """
        inherit HR Employee to add get_employee_child method
    """
    _inherit = 'hr.employee'

    job_level_id = fields.Many2one(
        'hr.job.level',
        related='job_id.job_level_id',
        string="Job Level",
        groups="hr.group_hr_user",  # to avoid using in employee public
        readonly=True, store=True
    )
    job_schema = fields.Selection(
        related='job_level_id.schema',
        string="Schema",
        groups="hr.group_hr_user",  # to avoid using in employee public
        readonly=True, store=True
    )

    @api.model
    def get_employees(self, domain):
        """
        Get all employees accord to domain
        :param domain: list of domain
        :return : list of employees
        """
        employees = self.env['hr.employee'].search(domain)
        groups = defaultdict(list)
        for emp in employees:
            if emp.job_level_id:
                groups[emp.job_level_id.code].append({
                    'id': emp.id,
                    'name': emp.name,
                    'image_1920': emp.image_1920,
                    'job_title': emp.job_title,
                    'job_level': emp.job_level_id.name,
                })
        listgroups = []
        for group in groups.items():
            listgroups.append(group)
        listgroups = sorted(listgroups, key=lambda x: x[0])

        return listgroups

    @api.model
    def get_employee_childs(self, employee):
        """
        recursively generate employee childs
        :param emp: `hr.employee` object
        :return : `index [0]` is employee itself `index [1]` list of its childs
        """
        if not employee:
            employee = self.env['hr.employee'].sudo().search([
                ('parent_id', '=', False)
            ])
            return [({
                'id': emp.id,
                'name': emp.name,
                'image_1920': emp.image_1920,
                'job_title': emp.job_title,
            }, [self.get_employee_childs(child)
                for child in emp.child_ids]) for emp in employee]
        return ({
            'id': employee.id,
            'name': employee.name,
            'image_1920': employee.image_1920,
            'job_title': employee.job_title
        }, [self.get_employee_childs(employee)
            for employee in employee.child_ids])

    @api.model
    def get_schema(self):
        """
        Get all employees accord to schema
        :return : list of schema and its employees
        """
        employees = self.env['hr.employee'].search([])

        def defualtlists():
            """ default list schema """
            return ["", 0, ""]

        sorted_schema = {"top": 0, "mid": 1, "staff": 2}
        groups = defaultdict(defualtlists)
        for emp in employees:
            if emp.job_level_id:
                schema = dict(self._fields['job_schema']
                              .selection(self))[emp.job_schema]
                groups[sorted_schema[emp.job_schema]][0] = schema
                groups[sorted_schema[emp.job_schema]][1] += 1
                groups[sorted_schema[emp.job_schema]][2] = \
                    ['job_schema', '=', emp.job_schema]
        listgroups = []
        for group in OrderedDict(sorted(groups.items())).items():
            listgroups.append(group)
        return listgroups
