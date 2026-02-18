""" Initialize Loan Config Settings. """
from odoo import fields, models


class LoanConfigSettings(models.TransientModel):
    """
        Initialize loan configuration:
         - separated configuration model.
         - allow hr manager to set configuration for loan requests.
    """
    _name = 'loan.config.settings'
    _description = 'Loan Config Settings'

    company_id = fields.Many2one(
        'res.company', default=lambda self: self.env.company
    )
    loan_type = fields.Selection(related='company_id.loan_type', readonly=False)
    loan_max = fields.Float(related='company_id.loan_max', readonly=False)
    loan_max_months = fields.Integer(
        related='company_id.loan_max_months', readonly=False,
    )
    loan_contract_months = fields.Integer(
        related='company_id.loan_contract_months', readonly=False,
    )
    loan_allow_multiple = fields.Boolean(
        related='company_id.loan_allow_multiple', readonly=False,
    )
    loan_approve = fields.Boolean(
        related='company_id.loan_approve', readonly=False,
    )
    loan_hr_user_id = fields.Many2one(related='company_id.loan_hr_user_id',
                                      readonly=False)
    loan_journal_id = fields.Many2one(related='company_id.loan_journal_id',
                                      readonly=False)
    loan_account_id = fields.Many2one(related='company_id.loan_account_id',
                                      readonly=False)