""" inherit Res Company to add loan configuration related with company. """
from odoo import fields, models


class ResCompany(models.Model):
    """
        inherit Res Company:
         - add loan configuration related with company.
    """
    _inherit = 'res.company'

    def _default_domain_member_ids(self):
        """ return list of users has group manager """
        group = self.env.ref('hr.group_hr_user')
        return [('groups_id', 'in', group.id)]

    loan_type = fields.Selection(
        [('amount', 'Amount'), ('percentage', 'Percentage')]
    )
    loan_max = fields.Float()
    loan_max_months = fields.Integer(help='Max number of installments')
    loan_contract_months = fields.Integer(
        string='Contract Months',
        help='Number of months after running contract allow request loan'
    )
    loan_allow_multiple = fields.Boolean(
        string='Allow Multiple loans',
        help='User will be able to request multiple loan at the same time.'
    )
    loan_approve = fields.Boolean(
        string='Approval from Accounting Department',
        help='Account manager will approve loan request.'
    )
    loan_hr_user_id = fields.Many2one(
        comodel_name='res.users', string='HR Responsible',
        domain=lambda self: self._default_domain_member_ids(),
        help='user will get notify when loan is submitted')
    loan_journal_id = fields.Many2one(
        'account.journal', 'Default Loan Journal', company_dependent=True,
        default=lambda self: self.env['account.journal'].sudo().search(
            [('type', '=', 'general'),
             ('company_id', '=', self.env.company.id)],
            limit=1))
    loan_account_id = fields.Many2one(
        comodel_name='account.account', string='Default Loan Account',
        company_dependent=True, required=False)

