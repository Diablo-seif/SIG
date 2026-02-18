""" init hr.contract.wage.calculate """
from odoo import api, fields, models


class HrContractWageCalculate(models.TransientModel):
    _name = 'hr.contract.wage.calculate'
    _description = 'Calculate Gross Amount Based on Net Wizard'

    net_amount = fields.Float()
    with_social_insurance = fields.Boolean(
        string='Without Social Insurance',
    )
    insurance_amount = fields.Float()
    insurance_employee_percentage = fields.Float(
        default=11,
    )
    tax_type = fields.Selection(
        selection=[
            ('laws', 'Laws'),
            ('percentage', 'Percentage'),
        ],
        required=True,
        string='Tax Type',
        default='laws',
    )
    hr_salary_tax_id = fields.Many2one('hr.salary.tax', string='Tax Law',)
    fixed_percentage = fields.Float(
        default=10,
    )
    gross_amount = fields.Float(
        compute="_compute_gross_amount",
    )
    
    @api.depends('net_amount', 'tax_type', 'fixed_percentage',
                 'insurance_amount', 'with_social_insurance',
                 'insurance_employee_percentage','hr_salary_tax_id')
    def _compute_gross_amount(self):
        """
        calculate gross amount on fly
        """
        for record in self:
            record.gross_amount = record._get_gross_amount()

    def action_calculate_gross_amount(self):
        """
        calculate amount and update contract
        """
        active_ids = self.env.context.get('active_ids')
        contracts = self.env['hr.contract'].browse(active_ids)
        gross_amount = self._get_gross_amount()
        contracts.write({
            'wage': gross_amount,
            'eg_net_amount': self.net_amount,
            'eg_with_social_insurance': self.with_social_insurance,
            'eg_insurance_amount': self.insurance_amount,
            'eg_insurance_employee_percentage':
                self.insurance_employee_percentage,
            'eg_tax_type': self.tax_type,
            'eg_fixed_percentage': self.fixed_percentage,
            'hr_salary_tax_id': self.hr_salary_tax_id,
            
        })

    def _get_gross_amount(self):
        """
        return gross amount based on calculation
        """
        if self.tax_type == 'percentage':
            return self._calculate_tax_percentage()
        # elif self.tax_type == 'egypt_law':
        #     return self._calculate_tax_egypt_law()
        elif self.tax_type == 'laws':
            return self._calculate_tax_egypt_law_23()

    def _calculate_tax_percentage(self):
        """
        return gross amount based on net amount and insurance amount
        """
        percentage = self.fixed_percentage / 100
        gross_amount = self.net_amount / (1 - percentage)

        if not self.with_social_insurance:
            return gross_amount
        insurance_employee_share = self.insurance_amount * \
                                   (self.insurance_employee_percentage / 100)
        return gross_amount + insurance_employee_share

    def _calculate_tax_egypt_law(self):
        """
        return gross amount based on net amount and egypt law 2020
        """
        if not self.with_social_insurance:
            insurance_employee_share = \
                self.insurance_amount * (self.insurance_employee_percentage / 100)
            net_amount = (self.net_amount * 12) - 9000 + (
                    insurance_employee_share * 12)
        else:
            net_amount = (self.net_amount * 12) - 9000
        gross_amount = 0
        if net_amount <= 15000:
            gross_amount = net_amount
        elif net_amount <= 29625:
            gross_amount = (net_amount * 100 / 97.5) - 375 - 9.61538461538294
        elif net_amount <= 43125:
            gross_amount = (net_amount * 100 / 90) - 2625 - 291.666666666664
        elif net_amount <= 55875:
            gross_amount = (net_amount * 100 / 85) - 4875 - 860.294117647063
        elif net_amount <= 167875:
            gross_amount = (net_amount * 100 / 80) - 7875 - 1968.75
        elif net_amount <= 322875:
            gross_amount = (net_amount * 100 / 77.5) - 12875 - 3737.90322580643
        elif net_amount <= 472875:
            gross_amount = (net_amount * 100 / 75) - 22875 - 7625
        elif net_amount <= 547500:
            gross_amount = (net_amount * 100 / 75) - 22500 - 7500
        elif net_amount <= 620250:
            gross_amount = (net_amount * 100 / 75) - 20250 - 6750
        elif net_amount <= 693000:
            gross_amount = (net_amount * 100 / 75) - 18000 - 6000
        elif net_amount <= 765000:
            gross_amount = (net_amount * 100 / 75) - 15000 - 5000
        elif net_amount > 760000:
            gross_amount = (net_amount * 100 / 75) - 10000 - 3333.33333333325
        gross_monthly = (gross_amount + 9000) / 12
        if not self.with_social_insurance:
            return gross_monthly
        insurance_employee_share = \
            self.insurance_amount * (self.insurance_employee_percentage / 100)
        return gross_monthly + insurance_employee_share

    def _calculate_tax_egypt_law_23(self):
        """
        return gross amount based on net amount and egypt law 2023
        """

        if self.hr_salary_tax_id.python_code_from_net_to_gross:
            parameters = {
            'insurance_amount': self.insurance_amount,
            'insurance_employee_percentage': self.insurance_employee_percentage,
            'net_amount': self.net_amount,
            'with_social_insurance': self.with_social_insurance
            }
            global_namespace = {}
            exec(self.hr_salary_tax_id.python_code_from_net_to_gross, global_namespace, parameters)
            returned_fields = parameters.get('result', [])
            return returned_fields
        return 0

    @api.onchange('with_social_insurance')
    def _onchange_with_social_insurance(self):
        """
        reset insurance amount
        """
        self.insurance_amount = 0
