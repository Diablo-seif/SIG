""" Initialize Insurance Sector Period """

from odoo import _, api, fields, models

from odoo.exceptions import ValidationError


class InsuranceSectorPeriod(models.Model):
    """ insurance Sectors period """
    _name = "insurance.sector.period"
    _description = 'Insurance Period Details'
    _inherit = 'hr.period'

    employee_percentage = fields.Float()
    company_percentage = fields.Float()
    sector_id = fields.Many2one(
        'insurance.sector'
    )
    sector_line_ids = fields.One2many(
        'insurance.sector.line',
        'sector_id',
        string='Insurance Details'
    )

    @api.constrains('date_from', 'date_to')
    def _check_date(self):
        """ Validate date overlaps """
        for record in self:
            start = record.date_from
            end = record.date_to
            overlaps = self.search([
                ('id', '!=', record.id),
                ('sector_id', '=', record.sector_id.id),
                '|', '&',
                ('date_from', '<=', start), ('date_to', '>=', start), '&',
                ('date_from', '<=', end), ('date_to', '>=', end),
            ])
            if overlaps:
                raise ValidationError(
                    _('Period is overlapped')
                )

    @api.constrains('sector_line_ids', 'employee_percentage',
                    'company_percentage')
    def _check_sector_line_percentage(self):
        """ Validate sector_line_percentage """
        for rec in self:
            employee_percentage = sum(
                rec.sector_line_ids.mapped('employee_percentage'))
            company_percentage = sum(
                rec.sector_line_ids.mapped('company_percentage'))
            if rec.employee_percentage != employee_percentage:
                raise ValidationError(
                    _('Total employee percentage lines must be equal to %s') %
                    rec.employee_percentage
                )
            if rec.company_percentage != company_percentage:
                raise ValidationError(
                    _('Total company percentage lines must be equal to %s') %
                    rec.company_percentage
                )
