
from odoo import models, fields, api


class HrPayslip(models.Model):

    
    _inherit = 'hr.payslip'

    social_insurance_salary = fields.Monetary(compute="_compute_salary_columns", store=True, readonly=False)
    gross = fields.Monetary(compute="_compute_salary_columns", store=True, readonly=False)
    social_insurance_company_share = fields.Monetary(compute="_compute_salary_columns", store=True, readonly=False)
    social_insurance_employee_share = fields.Monetary(compute="_compute_salary_columns", store=True, readonly=False)
    total_recurring_deductions = fields.Monetary(compute="_compute_salary_columns", store=True, readonly=False)
    net_taxable_salary = fields.Monetary(compute="_compute_salary_columns", store=True, readonly=False)
    deduction_leave = fields.Monetary(compute="_compute_salary_columns", store=True, readonly=False)
    management_penalty = fields.Monetary(compute="_compute_salary_columns", store=True, readonly=False)
    tardiness = fields.Monetary(compute="_compute_salary_columns", store=True, readonly=False)
    unattended_days = fields.Monetary(compute="_compute_salary_columns", store=True, readonly=False)
    absence_penalties = fields.Monetary(compute="_compute_salary_columns", store=True, readonly=False)
    loan = fields.Monetary(compute="_compute_salary_columns", store=True, readonly=False)
    
    basic_wage = fields.Monetary(store=True, readonly=False)
    net_wage = fields.Monetary(store=True, readonly=False)
    
    other_allowance = fields.Monetary(compute="_compute_salary_columns", store=True, readonly=False)
    transportation_allowances = fields.Monetary(compute="_compute_salary_columns", store=True, readonly=False)
    incentives = fields.Monetary(compute="_compute_salary_columns", store=True, readonly=False)
    special_bonus = fields.Monetary(compute="_compute_salary_columns", store=True, readonly=False)
    medical_insurance = fields.Monetary(compute="_compute_salary_columns", store=True, readonly=False)
    addition = fields.Monetary(compute="_compute_salary_columns", store=True, readonly=False)
    martyrs_fund = fields.Monetary(compute="_compute_salary_columns", store=True, readonly=False)
    other_deduction = fields.Monetary(compute="_compute_salary_columns", store=True, readonly=False)
    un_working_contract_days_penalties = fields.Monetary(compute="_compute_salary_columns", store=True, readonly=False)
    total_other_deductions = fields.Monetary(compute="_compute_salary_columns", store=True, readonly=False)
    allowance = fields.Monetary(compute="_compute_salary_columns", store=True, readonly=False)
    salary_tax = fields.Monetary(compute="_compute_salary_columns", store=True, readonly=False)
    basic = fields.Monetary(compute="_compute_salary_columns", store=True, readonly=False)
    net_before_tax = fields.Monetary(compute="_compute_salary_columns", store=True, readonly=False)
    net_salary = fields.Monetary(compute="_compute_salary_columns", store=True, readonly=False)
    total_cost = fields.Monetary(compute="_compute_salary_columns", store=True, readonly=False)

    
    @api.depends('line_ids')
    def _compute_salary_columns(self):
        line_values = (self._origin)._get_line_values(['BASICIN', 'GROSS','SICS',
            'SOIN', 'TRD', 'NETUNT', 'PENALTY_DED_LEV', 'PENALTY_DED_MAN', 'PENALTY_DED_TAR',
            'PENALTY_DED_UIO', 'PENALTY_DED_ABP', 'LO', 'OA', 'BO', 'SB', 'MEA', 'ADD', 'MFDED',
            'NONDED', 'PENALTY_DED_UNW', 'TOD', 'BA', 'ST', 'BASIC55', 'NBTBT', 'NET', 'TOTAL_COST'])
        
        for payslip in self:
            payslip.social_insurance_salary = line_values['BASICIN'][payslip._origin.id]['total']
            payslip.gross = line_values['GROSS'][payslip._origin.id]['total']
            payslip.social_insurance_company_share = line_values['SICS'][payslip._origin.id]['total']
            payslip.social_insurance_employee_share = line_values['SOIN'][payslip._origin.id]['total']
            payslip.total_recurring_deductions = line_values['TRD'][payslip._origin.id]['total']
            payslip.net_taxable_salary = line_values['NETUNT'][payslip._origin.id]['total']  
            payslip.deduction_leave = line_values['PENALTY_DED_LEV'][payslip._origin.id]['total']
            payslip.management_penalty = line_values['PENALTY_DED_MAN'][payslip._origin.id]['total']
            payslip.tardiness = line_values['PENALTY_DED_TAR'][payslip._origin.id]['total']
            payslip.unattended_days = line_values['PENALTY_DED_UIO'][payslip._origin.id]['total']
            payslip.absence_penalties = line_values['PENALTY_DED_ABP'][payslip._origin.id]['total']
            payslip.loan = line_values['LO'][payslip._origin.id]['total']
            payslip.other_allowance = line_values['OA'][payslip._origin.id]['total']
            payslip.transportation_allowances = line_values['TA'][payslip._origin.id]['total']
            payslip.incentives = line_values['BO'][payslip._origin.id]['total']
            payslip.special_bonus = line_values['SB'][payslip._origin.id]['total']
            payslip.medical_insurance = line_values['MEA'][payslip._origin.id]['total']
            payslip.addition = line_values['ADD'][payslip._origin.id]['total']
            payslip.martyrs_fund = line_values['MFDED'][payslip._origin.id]['total']
            payslip.other_deduction = line_values['NONDED'][payslip._origin.id]['total']
            payslip.un_working_contract_days_penalties = line_values['PENALTY_DED_UNW'][payslip._origin.id]['total']
            payslip.total_other_deductions = line_values['TOD'][payslip._origin.id]['total']
            payslip.allowance = line_values['BA'][payslip._origin.id]['total']
            payslip.salary_tax = line_values['ST'][payslip._origin.id]['total']
            payslip.basic = line_values['BASIC55'][payslip._origin.id]['total']
            payslip.net_before_tax = line_values['NBTBT'][payslip._origin.id]['total']
            payslip.net_salary = line_values['NET'][payslip._origin.id]['total']
            payslip.total_cost = line_values['TOTAL_COST'][payslip._origin.id]['total']
            
            