""" Initialize Res Settings """

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    """
        Inherit Res Config Settings:
         - 
    """
    _inherit = 'res.config.settings'

    overtime_type = fields.Selection(
        related='company_id.overtime_type', readonly=False
    )
    compensatory_percent = fields.Float(
        related='company_id.compensatory_percent', readonly=False
    )
    overtime_leave_type_id = fields.Many2one(
        'hr.leave.type', related='company_id.overtime_leave_type_id',
        readonly=False
    )

    @api.onchange('overtime_leave_type_id')
    def _onchange_overtime_leave_type_id(self):
        """ overtime_leave_type_id """
        if self.overtime_leave_type_id.id:
            if self.overtime_leave_type_id.request_unit != 'hour':
                raise ValidationError(_(
                    "Must Be Select (Take Time Off in) Field in  (Overtime Leave Type)  default Hours"))
        else:
            pass
