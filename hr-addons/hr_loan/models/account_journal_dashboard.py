""" Inherit account.journal to link with loans. """
from odoo import models
from odoo.tools.misc import formatLang


# pylint: disable=no-member
class AccountJournal(models.Model):
    """
            Inherit account journal:
             - Link with loans
        """
    _inherit = "account.journal"

    def _get_loans_to_pay_query(self):
        """
        Returns a tuple containing as it's first element the SQL query used to
        gather the loans in reported state data, and the arguments
        dictionary to use to run it as it's second.
        """
        query = """SELECT loan_amount as amount_total, currency_id AS currency
                  FROM hr_loan
                  WHERE state IN ('waiting_approval_2', 'approve')
                  and payments_paid = FALSE and journal_id = %(journal_id)s"""
        return (query, {'journal_id': self.id})

    def get_journal_dashboard_datas(self):
        """ appear loan info in journal dashboard """
        res = super(AccountJournal, self).get_journal_dashboard_datas()
        # add the number and sum of expenses to pay to the json defining
        # the accounting dashboard data
        (query, query_args) = self._get_loans_to_pay_query()
        self.env.cr.execute(query, query_args)
        query_results_to_pay = self.env.cr.dictfetchall()
        (number_to_pay, sum_to_pay) = self._count_results_and_sum_amounts(
            query_results_to_pay, self.company_id.currency_id)
        res['number_loans_to_pay'] = number_to_pay
        currency = self.currency_id or self.company_id.currency_id
        res['sum_loans_to_pay'] = \
            formatLang(self.env, sum_to_pay or 0.0,
                       currency_obj=currency)
        return res

    def open_loans_action(self):
        """ allow open pending loans """
        action = self.env['ir.actions.act_window']._for_xml_id(
            'hr_loan.hr_loan_action')
        action['context'] = {
            'search_default_account_pay': 1,
            'search_default_account_approval': 1,
            'search_default_journal_id': self.id,
            'default_journal_id': self.id,
        }
        action['view_mode'] = 'list,form'
        action['views'] = [(k, v) for k, v in action['views'] if
                           v in ['list', 'form']]
        return action
