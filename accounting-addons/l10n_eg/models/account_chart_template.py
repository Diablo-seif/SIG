"""inherit model account.chart.template"""
from odoo import models


class AccountChartTemplate(models.Model):
    """
    inherit model account.chart.template
    to add some journals
    """
    _inherit = 'account.chart.template'

    # pylint: disable=no-member
    def _prepare_all_journals(self, acc_template_ref, company,
                              journals_dict=None):
        """
        override _prepare_all_journals
        to add new journals data to create it
        """
        res = super(AccountChartTemplate, self)._prepare_all_journals(
            acc_template_ref, company, journals_dict=journals_dict
        )
        self.ensure_one()
        if self == self.env.ref('l10n_eg.l10n_eg_account_chart_template'):
            res += [
                {
                    'type': 'general',
                    'name': 'Fixed Assets Journal',
                    'code': 'FAJ', 'company_id': company.id,
                    'show_on_dashboard': True,
                },
                {
                    'type': 'general',
                    'name': 'Capital and Inertial Balance Journal',
                    'code': 'CAIBJ',
                    'company_id': company.id,
                    'show_on_dashboard': True,
                },
                {
                    'type': 'cash',
                    'name': 'Withholding Tax Journal',
                    'code': 'WTJ',
                    'taxation': True,
                    'tax_type': 'withholding',
                    'company_id': company.id,
                    'show_on_dashboard': True,
                },
                {
                    'type': 'cash',
                    'name': 'Deduction Tax Journal',
                    'code': 'DTJ',
                    'taxation': True,
                    'tax_type': 'deduction',
                    'company_id': company.id,
                    'show_on_dashboard': True,
                },
                {
                    'type': 'cash',
                    'name': 'Custody and Petty Cash',
                    'code': 'CAPC',
                    'company_id': company.id,
                    'show_on_dashboard': True,
                },
            ]
        return res
