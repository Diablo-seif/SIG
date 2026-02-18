""" init hr.payslip.payment.method """
from odoo import fields, models


class HrPayslipPaymentMethod(models.Model):
    """
    init hr.payslip.payment.method
    """
    _name = 'hr.payslip.payment.method'
    _description = 'Hr Payslip Payment Method'

    name = fields.Char(
        required=True,
    )
    active = fields.Boolean(
        default=True,
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        default=lambda self: self.env.company,
        required=True,
    )
