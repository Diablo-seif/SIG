""" init object res.config.settings"""

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ResConfigSettings(models.TransientModel):
    """ init object  res.config.settings"""
    _inherit = 'res.config.settings'

    @api.constrains('midday_time')
    def _constrains_midday_time(self):
        """
        Constrains Midday Time.
        """
        self.ensure_one()
        max_hours = round(float(float(58.0 / 60.0) + 23.0), 2)
        if self.midday_time < 0.0 or self.midday_time > max_hours:
            raise UserError(_("Midday Time Must Be In Range [00:00 to 23:57]."))

    @api.constrains('day_start_month')
    def _constrains_day_start_month(self):
        """
        Constrains start day of month.
        """
        self.ensure_one()
        if self.day_start_month < 1 or self.day_start_month > 28:
            raise UserError(_("Start Day In Month Must Be In Range [1 to 28]."))

    # pylint: disable=no-member, missing-return
    def set_values(self):
        """
        Override Set Value
        """
        super(ResConfigSettings, self).set_values()
        if not self.missing_without_delay_in:
            missing_without_delay_in = "false"
        else:
            missing_without_delay_in = "true"
        if not self.missing_without_early_out:
            missing_without_early_out = "false"
        else:
            missing_without_early_out = "true"

        self.env['ir.config_parameter'].sudo().set_param(
            "missing_without_delay_in", missing_without_delay_in
        )
        self.env['ir.config_parameter'].sudo().set_param(
            "missing_without_early_out", missing_without_early_out
        )

    # pylint: disable=no-member
    @api.model
    def get_values(self):
        """
        Override Get Value
        """
        res = super(ResConfigSettings, self).get_values()
        config_obj = self.env['ir.config_parameter'].sudo()
        missing_without_delay_in_str = config_obj.get_param(
            'missing_without_delay_in')
        missing_without_early_out_str = config_obj.get_param(
            'missing_without_early_out')

        missing_without_delay_in = False
        missing_without_early_out = False
        if missing_without_delay_in_str in ["true", "True", "1"]:
            missing_without_delay_in = True
        if missing_without_early_out_str in ["true", "True", "1"]:
            missing_without_early_out = True

        res.update(
            missing_without_delay_in=missing_without_delay_in,
            missing_without_early_out=missing_without_early_out
        )
        return res

    day_start_month = fields.Integer(
        config_parameter='day_start_month'
    )
    midday_time = fields.Float(config_parameter='midday_time')
    start_month = fields.Selection(
        default="current",
        selection=[('current', 'Current Month'),
                   ('previous', 'Previous Month')],
        config_parameter='start_month'
    )
    missing_without_delay_in = fields.Boolean(
        config_parameter='missing_without_delay_in'
    )
    missing_without_early_out = fields.Boolean(
        config_parameter='missing_without_early_out'
    )
