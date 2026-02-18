
from odoo import fields, models, api


class DepartmentBudgetLine(models.Model):

    _name = "department.budget.line"

    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)
    actual_cost = fields.Float(compute="_compute_actual_cost")    
    budget = fields.Float(required=True)
    difference = fields.Float(compute="_compute_difference")
    department_id = fields.Many2one('hr.department', required=True)
    po_number = fields.Char(string="PO Number")
    proposal_id = fields.Many2one(
        'proposal.proposal',
        domain=[('is_outsourcing', '=', True)]
    )
    
    def _compute_actual_cost(self):
        for record in self:
           record.actual_cost = sum(self.env['hr.payslip'].sudo().search([
                ('date_from', '=', record.date_from),
                ('date_to', '=', record.date_to),
                ('department_id', '=', record.department_id.id)
            ]).mapped('total_cost'))

    @api.depends('actual_cost', 'budget')
    def _compute_difference(self):
        for record in self:
            record.difference = record.budget - record.actual_cost
