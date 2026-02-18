""" Inherit hr.employee """

from datetime import datetime
from odoo import fields, models, api


class HrEmployee(models.Model):
    """
        inherit hr.employee:
    """
    _inherit = 'hr.employee'

    type = fields.Selection([
        ('external', 'External'),
        ('internal', 'Internal')], required=True)
    employee_type_id = fields.Many2one('employee.type', domain="[('type', '=', type)]")
    blood_type = fields.Selection([('a+', 'A+'), ('a-', 'A-'),
                                   ('b+', 'B+'), ('b-', 'B-'),
                                   ('o+', 'O+'), ('o-', 'O-'),
                                   ('ab+', 'AB+'), ('ab-', 'AB-')])
    bank_account_1 = fields.Char()
    bank_account_2 = fields.Char()
    social_insurance = fields.Char()
    social_insurance_number = fields.Char()
    military_status = fields.Char()
    graduation_certificate = fields.Char()
    military_certificate = fields.Char()
    criminal_status = fields.Char()
    birth_certificate = fields.Char()
    employee_contract = fields.Char()
    manpower_office_form = fields.Char()
    social_insurance_print = fields.Char()
    medical_test_111_form = fields.Char()
    social_status_statement = fields.Char()
    organization_policies = fields.Char()
    photos = fields.Char()
    marital_status_arabic = fields.Char()
    graduation_degree = fields.Char()
    year_of_graduation = fields.Char()
    # first_contract_date = fields.Char()
    registration_number_of_the_employee = fields.Char()
    access_tags_ids = fields.Many2many(
        'access.tags',
        domain=lambda self: [('id', 'in', self.env.user.access_tags_ids.ids)],
        required=True
    )
    state_id = fields.Many2one(
        'res.country.state', 
        string="Governorate",
        domain="[('country_id', '=', 65)]"
    )
    zone_id = fields.Many2one(
       'res.country.zone',
       domain="[('state_id', '=?', state_id)]"
    )
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        domain="[('type', '=', type)]"
    )
    office_id = fields.Many2one(
        'hr.office',
    )
    insured = fields.Boolean(default=False)
    birthday = fields.Date(compute="_compute_birthday")
    age = fields.Integer(compute="_compute_age")
    barcode = fields.Char(string="Employee Code")
    identification_id = fields.Char(string="National ID")
    parent_id = fields.Many2one('hr.employee', 'Manager',
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    
    @api.depends('identification_id')
    def _compute_birthday(self):
        for record in self:
            if record.identification_id:
                year = ""
                if record.identification_id[0] == "3":
                    year = "20"
                if record.identification_id[0] == "2":
                    year = "19"
                year += record.identification_id[1] + record.identification_id[2]
                month = record.identification_id[3] + record.identification_id[4]
                day = record.identification_id[5] + record.identification_id[6]
                
                date_string = year + "-" + month + "-" + day  
                if 0 < int(month) < 13 and 0 < int(day) < 31:              
                    record.birthday = datetime.strptime(date_string, "%Y-%m-%d")
                else:
                    record.birthday = False
            else:
                record.birthday = False

    @api.depends('department_id')
    def _compute_parent_id(self):
        for employee in self:
            if not employee.parent_id:
                employee.parent_id = False
            
    @api.depends('age')
    def _compute_age(self):
        for record in self:
            if record.birthday:
                current_date = datetime.now().date()
                record.age = current_date.year - record.birthday.year - ((current_date.month, current_date.day) < (record.birthday.month, record.birthday.day))
            else:
                record.age = False       
                

