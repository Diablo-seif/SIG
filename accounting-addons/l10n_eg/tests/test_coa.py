"""Chart Of Account Test Cases"""

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class ChartOfAccountTest(TransactionCase):
    """Chart Of Account Test Cases"""

    # pylint: disable=too-many-locals
    def test_01_deduction_tax_vendor(self):
        """
        Test Scenario: create company to load chart of account for it
        then check if it has accounts
        """
        chart_template = self.env.ref('l10n_eg.l10n_eg_account_chart_template')
        new_company = self.env['res.company'].create({
            'name': "new company",
        })
        self.env.user.company_ids |= new_company
        self.env.user.company_id = new_company
        chart_template.try_loading()
        accounts = self.env['account.account'].search(
            [('company_id', '=', new_company.id)])
        self.assertTrue(accounts)
