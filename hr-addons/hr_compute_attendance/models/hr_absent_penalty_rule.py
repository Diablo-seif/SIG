""" init module hr.absent.penalty.rule and hr.absent.penalty.redundant"""

from odoo import fields, models


class HrAbsentPenaltyRules(models.Model):
    """ init module hr.absent.penalty.rule"""
    _name = 'hr.absent.penalty.rule'
    _description = 'Absent Penalty Rule'

    _description = 'hr absent penalty rules'
    _order = 'redundant asc'
    _inherit = ['mail.thread']

    calendar_id = fields.Many2one('resource.calendar', 'Working Schedule')
    redundant = fields.Integer(default=1, required=True)
    absent_value = fields.Float(required=True, string='Absent Percentage')
