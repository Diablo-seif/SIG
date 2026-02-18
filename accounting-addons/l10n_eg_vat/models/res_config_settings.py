""" init module res.config.settings"""

from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    """ init module res.config.settings"""

    _inherit = 'res.config.settings'

    vat_warning_day = fields.Integer(
        "VAT warning Delay",
        help="# day accountant should check the VAT report",
        related='company_id.vat_warning_day',
        readonly=False
    )
    vat_email_interval_number = fields.Integer(
        default=1,
        string="Repeat every",
        help="Repeat Send VAT Report Check every",
    )
    vat_email_interval_type = fields.Selection(
        [('days', 'Days'), ('weeks', 'Weeks')],
        string='VAT Email Interval Unit',
        default='days'
    )
    module_l10n_eg_tax_included_in_price = fields.Boolean(
        string="Tax included in price"
    )

    # pylint: disable=no-member
    @api.model
    def get_values(self):
        """  read cron job intervals data """
        res = super(ResConfigSettings, self).get_values()
        vat_cron = self.env.ref('l10n_eg_vat.vat_warning_monthly_cron')
        if vat_cron:
            res.update(vat_email_interval_number=vat_cron.interval_number)
            res.update(vat_email_interval_type=vat_cron.interval_type)
        return res

    # pylint: disable=no-member
    def set_values(self):
        """  set cron job intervals data """
        res = super(ResConfigSettings, self).set_values()
        vat_cron = self.env.ref('l10n_eg_vat.vat_warning_monthly_cron')
        if vat_cron:
            vat_cron.write({'interval_number': self.vat_email_interval_number,
                            'interval_type': self.vat_email_interval_type})
        return res
