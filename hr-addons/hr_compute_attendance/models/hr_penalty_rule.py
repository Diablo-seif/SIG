""" init module hr.penalty.rule and hr.penalty.redundant"""

from odoo import _, api, fields, models
from odoo.exceptions import UserError

PENALTY_TYPE_SELECTION = [('late_in', 'Late In'),
                          ('early_out', 'Early Out'),
                          ('missing_hours', 'Missing Hours'), ]


class HrPenaltyRules(models.Model):
    """ init module hr.penalty.rule"""
    _name = 'hr.penalty.rule'
    _description = 'hr penalty rules'
    _inherit = ['mail.thread']

    def get_penalty_value_redundant(self, redundant=0):
        """
        Get Penalty value of redundant.
        :param redundant:<integer>
        :return: <float> value of penalty.
        """
        if redundant > 0 and self.penalty_redundant_ids:
            redundant_id = self.penalty_redundant_ids.filtered(
                lambda x: x.redundant == redundant)
            max_redundant_id = self.penalty_redundant_ids \
                .sorted(key=lambda x: x.redundant * -1)[0]
            max_redundant = max_redundant_id.redundant
            if redundant > max_redundant:
                redundant_id = max_redundant_id
            if redundant_id:
                return redundant_id[0].penalty_value
        return 0

    # pylint: disable=no-member
    @api.constrains('delay_from', 'delay_to', 'calendar_id')
    def _constrains_penalty_overlab(self):
        """
        Constrain to Overlaps penalty rules.
        """
        for record in self:
            penalty_type = record.penalty_type
            delay_from = record.delay_from
            delay_to = record.delay_to
            calendar_id = record.calendar_id
            data_count = self.search_count(
                [('calendar_id', '=', calendar_id.id),
                 ('penalty_type', '=', penalty_type),
                 ('delay_from', '<=', delay_to),
                 ('delay_to', '>=', delay_from),
                 ('id', '!=', record.id)]
            )
            penalty_types = dict(PENALTY_TYPE_SELECTION)
            if data_count:
                raise UserError(
                    _("You Cannot have 2 Penalty Rules that have"
                      " Overlaps on Minutes With Work schedule: %(name)s"
                      " and Penalty Type: %(type)s") % {
                          "name": calendar_id.name,
                          "type": penalty_types.get(penalty_type)
                      }
                )

    name = fields.Char(string="Title", required=True)
    delay_from = fields.Integer(string="Delay Minutes From", required=True)
    delay_to = fields.Integer(string="Delay Minutes To", required=True)
    penalty_type = fields.Selection(default='late_in', required=True,
                                    selection=PENALTY_TYPE_SELECTION)
    active = fields.Boolean(default=True)
    deduction_type = fields.Selection(
        selection=[('percentage', 'Percentage'),
                   ('fixed_amount', 'Fixed Amount')], required=True,
        default='percentage')
    penalty_redundant_ids = fields.One2many(comodel_name="hr.penalty.redundant",
                                            inverse_name="penalty_id",
                                            string="Penalty Redundant Lines")
    calendar_id = fields.Many2one(comodel_name="resource.calendar",
                                  string="Working Schedule", required=False)


class HrPenaltyRedundant(models.Model):
    """ init module penalty redundant"""
    _name = 'hr.penalty.redundant'
    _description = 'HR Penalty Redundant Lines'
    _order = 'redundant asc'

    def name_get(self):
        """
        Override Name Get.
        :return:<string> concatenate redundant and value.
        """
        result = []
        for rec in self:
            result.append((rec.id, "#%d=%s" % (rec.redundant,
                                               rec.penalty_value)))
        return result

    penalty_id = fields.Many2one(comodel_name="hr.penalty.rule",
                                 string="Penalty Rule")
    redundant = fields.Integer(default=1, required=True)
    penalty_value = fields.Float(required=True)
