
from odoo import fields, models, api
from datetime import datetime


class ProposalYearlyFinancial(models.Model):
     _name = 'proposal.yearly.financial'
     _description = 'proposal yearly financial'
     _check_company_auto = True
    
     proposal_id = fields.Many2one('proposal.proposal')
     date_order = fields.Date(
          related='proposal_id.date_order',
          string='Proposal Date',
          store=True
     )
     contract_date = fields.Date(
          related='proposal_id.contract_date',
          store=True
     )
     state = fields.Selection(
          related='proposal_id.state',
          store=True
     )
     project_progress = fields.Float(
          related='proposal_id.project_progress',
     )
     type = fields.Selection([('new', 'New'),
          ('old', 'Old')
     ])
     year = fields.Char()
     remaining_revenue = fields.Float()
     remaining_cost = fields.Float()
     remaining_margin = fields.Float(compute='_compute_remaining_margin', store=True)
     year_state = fields.Selection(
          [('current', 'Current'),
          ('previous', 'Previous')],
          compute='_compute_year_state',
     )
     company_id = fields.Many2one(
          related='proposal_id.company_id',
          store=True
     )
     cumulative_remaining_revenue = fields.Float()
     cumulative_remaining_cost = fields.Float()
     
     def _compute_year_state(self):
          current_year = datetime.today().year
          for record in self:
               if record.year == str(current_year):
                    record.year_state = 'current'
               else:
                    record.year_state = 'previous'

     @api.depends('remaining_revenue', 'remaining_cost')
     def _compute_remaining_margin(self):
          for rec in self:
              rec.remaining_margin = rec.remaining_revenue - rec.remaining_cost