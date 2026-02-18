""" Test BudgetImportTemplates """
from odoo.tests.common import TransactionCase


class TestBudgetImportTemplates(TransactionCase):
    """ Integration test for BudgetImportTemplates """

    def test_budget_import_templates(self):
        """ Test Scenario: budget_import_templates() """
        self.assertTrue(self.env['crossovered.budget'].get_import_templates())
