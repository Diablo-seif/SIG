""" inherit hr.contract """
from odoo import fields, models, api


class HrContract(models.Model):
    """
    inherit hr.contract
    """
    _inherit = 'hr.contract'

    eg_net_amount = fields.Float(
        string='Net Amount'
    )
    eg_with_social_insurance = fields.Boolean(
        string='Without Social Insurance',
    )
    eg_insurance_amount = fields.Float(
        string='Insurance Amount'
    )
    eg_insurance_employee_percentage = fields.Float(
        default=11,
        string='Insurance Employee Percentage'
    )
    eg_tax_type = fields.Selection(
        selection=[
            ('laws', 'Laws'),
            ('percentage', 'Percentage'),
        ],
        string='Tax Type',
        default='laws',
    )
    hr_salary_tax_id = fields.Many2one('hr.salary.tax', string='Tax Law',)
    eg_fixed_percentage = fields.Float(
        default=10,
        string='Fixed Percentage',
    )

    basic_salary = fields.Monetary(compute="_compute_salary_columns", store=True, readonly=False)
    allowance = fields.Monetary(compute="_compute_salary_columns", store=True, readonly=False)
    social_insurance_salary = fields.Monetary(compute="_compute_salary_columns", store=True, readonly=False)
    other_allowance = fields.Monetary(compute="_compute_salary_columns", store=True, readonly=False)
    transportation_allowance = fields.Monetary(compute="_compute_salary_columns", store=True, readonly=False)
    incentives = fields.Monetary(compute="_compute_salary_columns", store=True, readonly=False)
    special_bonus = fields.Monetary(compute="_compute_salary_columns", store=True, readonly=False)

    def open_calculate_net_to_gross_wizard(self):
        # return {
        #     'name': 'Calculate Net To Gross',
        #     'type': 'ir.actions.act_window',
        #     'view_mode': 'form',
        #     "view_type": "form",
        #     'res_model': 'hr.contract.wage.calculate',
        #     'target': 'new',
        #     'view_id': self.env.ref
        #     ('hr_contract_wage_eg_net_gross.hr_contract_wage_calculate_form').id,
        #     'context': {'active_ids': self.env.context.get('active_ids')},
        # }
        action = self.env["ir.actions.act_window"]._for_xml_id("hr_contract_wage_eg_net_gross.hr_contract_wage_calculate_action")
        action['context'] = repr(self.env.context)
        return action

    def action_calculate_incentives(self):
        for record in self:
            calculated_wage = sum(record.lines_ids.filtered(lambda r: r.code != "BASICIN").mapped('value'))
            if record.wage - calculated_wage != 0:
                incentives_line = record.lines_ids.filtered(lambda r: r.code == "BO")
                incentives_line.value += record.wage - calculated_wage

    def action_calculate_salary_input(self):
        for contract in self:
            for line in contract.lines_ids:
                line.unlink()
            salary_input = self.env['salary.input'].sudo().search([("code", '=', "BASIC01")], limit=1)
            self.env['salary.input.line'].sudo().create({
                "contract_id": contract.id,
                "name": salary_input.id,
                "value": contract.basic_salary
            })
            salary_input = self.env['salary.input'].sudo().search([("code", '=', "BA")], limit=1)
            self.env['salary.input.line'].sudo().create({
                "contract_id": contract.id,
                "name": salary_input.id,
                "value": contract.allowance
            })
            salary_input = self.env['salary.input'].sudo().search([("code", '=', "BASICIN")], limit=1)
            self.env['salary.input.line'].sudo().create({
                "contract_id": contract.id,
                "name": salary_input.id,
                "value": contract.social_insurance_salary
            })
            salary_input = self.env['salary.input'].sudo().search([("code", '=', "OA")], limit=1)
            self.env['salary.input.line'].sudo().create({
                "contract_id": contract.id,
                "name": salary_input.id,
                "value": contract.other_allowance
            })
            salary_input = self.env['salary.input'].sudo().search([("code", '=', "TA")], limit=1)
            self.env['salary.input.line'].sudo().create({
                "contract_id": contract.id,
                "name": salary_input.id,
                "value": contract.transportation_allowance
            })
            salary_input = self.env['salary.input'].sudo().search([("code", '=', "BO")], limit=1)
            self.env['salary.input.line'].sudo().create({
                "contract_id": contract.id,
                "name": salary_input.id,
                "value": contract.incentives
            })
            salary_input = self.env['salary.input'].sudo().search([("code", '=', "SB")], limit=1)
            self.env['salary.input.line'].sudo().create({
                "contract_id": contract.id,
                "name": salary_input.id,
                "value": contract.special_bonus
            })

    @api.depends('lines_ids')
    def _compute_salary_columns(self):
        for contract in self:
            for line in contract.lines_ids:
                if line.code == "BASIC01":
                    contract["basic_salary"] = line.value
                elif line.code == "BA":
                    contract["allowance"] = line.value
                elif line.code == "BASICIN":
                    contract["social_insurance_salary"] = line.value
                elif line.code == "OA":
                    contract["other_allowance"] = line.value
                elif line.code == "TA":
                    contract["transportation_allowance"] = line.value
                elif line.code == "BO":
                    contract["incentives"] = line.value
                elif line.code == "SB":
                    contract["special_bonus"] = line.value

