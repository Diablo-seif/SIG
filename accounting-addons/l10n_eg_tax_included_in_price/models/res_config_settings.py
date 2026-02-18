""" inherit res.config.settings to add tax_group_purchase_vat """

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    """
    inherit res.config.settings to add tax_group_purchase_vat
    """
    _inherit = 'res.config.settings'

    tax_group_purchase_vat_id = fields.Many2one(
        'account.tax.group',
        related='company_id.tax_group_purchase_vat_id',
        readonly=False,
        store=True,
    )
    fixed_assets_vat_id = fields.Many2one(
        'account.account',
        related='company_id.fixed_assets_vat_id',
        readonly=False,
        store=True,
    )
    cost_of_goods_sold_vat_id = fields.Many2one(
        'account.account',
        related='company_id.cost_of_goods_sold_vat_id',
        readonly=False,
        store=True,
    )
    expense_invest_vat_id = fields.Many2one(
        'account.account',
        related='company_id.expense_invest_vat_id',
        readonly=False,
        store=True,
    )
    expense_vat_id = fields.Many2one(
        'account.account',
        related='company_id.expense_vat_id',
        readonly=False,
        store=True,
    )

    # pylint: disable=no-member
    def set_values(self):
        """ override set values method to create included taxes """
        res = super(ResConfigSettings, self).set_values()
        self.env.company.create_included_taxes()
        return res
