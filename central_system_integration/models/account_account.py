from odoo import models, fields


class AccountAccount(models.Model):
    _inherit = "account.account"

    category = fields.Selection(
        [
            ("total_assets_non_current", "Non-Current Assets"),
            ("total_assets_current", "Current Assets"),
            ("total_capital", "Total Capital"),
            ("total_current_liabilities", "Total Current Liabilities"),
            ("total_non_current_liabilities", "Total Non-Current Liabilities"),
        ]
    )

    sub_category = fields.Selection(
        [
            ("fixed_asset_net", "Fixed Assets (Net)"),
            ("intangible_asset_net", "Intangible Assets (Net)"),
            ("project_under_process", "Projects Under Execution"),
            (
                "financial_investment_in_sister_companies",
                "Investments in Sister Companies",
            ),
            ("other_non_current_assets", "Other Non-Current Assets"),
            ("cash", "Cash and Cash Equivalents"),
            (
                "receivables_and_notes_receivable_account",
                "Receivables and Notes Receivable",
            ),
            ("account_receivable", "Account Receivable"),
            ("operations_under_process", "Operations Under Process"),
            ("paid_up_capital", "Paid Up Capital"),
            ("legal_reserve", "Legal Reserve"),
            ("retained_earning", "Retained Earnings"),
            ("current_earning", "Current Year Profit"),
            ("payables_and_notes_payable", "Payables and Notes Payable"),
            ("account_payable", "Account Payable"),
            ("non_current_liabilities", "Non-Current Liabilities"),
        ]
    )
