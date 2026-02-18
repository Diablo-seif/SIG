""" Abstract Period """

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


# pylint: disable=protected-access
class HrPeriod(models.AbstractModel):
    """ This model to use periods and validate that no overlaps or inverses """
    _name = 'hr.period'
    _description = 'Period'
    _sql_constraints = [(
        'date_from_before_date_to',
        'CHECK(date_from < date_to)',
        _('Date from must be anterior to the date to')
    )]
    date_from = fields.Date(
        required=True
    )
    date_to = fields.Date()
    period_month_ids = fields.One2many(
        'hr.period.month',
        'res_id',
        compute='_compute_period_months',
        store=True,
        auto_join=True,
        groups="base.group_user"
    )

    @api.depends('date_from', 'date_to')
    def _compute_period_months(self):
        """ get all months between date from and date to """
        for rec in self:
            date_to = rec.date_to or fields.Date.today()
            date_from = rec.date_from or fields.Date.today()
            period_months = (date_to.year - date_from.year) * 12 + \
                            (date_to.month - date_from.month)
            rec.period_month_ids = [(5, 0, 0)] + [(0, 0, {
                'name': (date_from +
                         relativedelta(months=month)).strftime('%b %Y'),
                'res_model_id': self.env['ir.model']._get(rec._name).id
            }) for month in range(period_months + 1)]

    def name_get(self):
        """ Override name_get to change displayed name """
        name = []
        for rec in self:
            name.append((rec.id,
                         _("%(model_name)s %(date_from)s "
                           "%(date_to)s") % {
                               "model_name": rec._description or '',
                               "date_from": rec.date_from or '',
                               "date_to":
                                   rec.date_to and '- %s' % rec.date_to or ''}))
        return name

    @api.constrains('date_from', 'date_to')
    def _check_date(self):
        """ Validate date overlaps """
        for record in self:
            start = record.date_from
            end = record.date_to
            overlaps = self.search([
                ('id', '!=', record.id),
                '|', '&',
                ('date_from', '<=', start), ('date_to', '>=', start), '&',
                ('date_from', '<=', end), ('date_to', '>=', end),
            ])
            if overlaps:
                raise ValidationError(
                    _('Period is overlapped')
                )


class HrPeriodMonth(models.Model):
    """ Period month """
    _name = 'hr.period.month'
    _description = 'Period Month'

    name = fields.Char()
    res_model_id = fields.Many2one(
        'ir.model', index=True, ondelete='cascade', required=True
    )
    res_model = fields.Char(
        related='res_model_id.model', compute_sudo=True,
        store=True, readonly=True
    )
    res_id = fields.Many2oneReference(
        index=True, required=True, model_field='res_model'
    )
