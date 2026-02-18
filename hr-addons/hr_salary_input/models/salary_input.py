"""Salary Input ORM Models"""
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SalaryInput(models.Model):
    """Salary Input Model"""
    _name = "salary.input"
    _description = "Salary Input"

    name = fields.Char(help='Name of Salary Input', required=True)
    code = fields.Char(required=True, help="Salary Input Code must be unique")

    _sql_constraints = [
        ('unique_code', 'UNIQUE(code)', 'Code must be unique')
    ]


class SalaryInputLine(models.Model):
    """ Salary Input Line"""
    _name = "salary.input.line"
    _description = "Salary Input Line"

    name = fields.Many2one('salary.input', 'Salary Input', required=True)
    code = fields.Char(related='name.code', readonly=True)
    contract_id = fields.Many2one('hr.contract', string='Contract')
    value = fields.Float()
    date_from = fields.Date()
    date_to = fields.Date()

    @api.constrains('date_from', 'date_to')
    def _validate_line_dates(self):
        """validate if date_from after date_to"""
        for rec in self:
            contract_date_end = rec.contract_id.date_end
            if rec.date_to:
                if not rec.date_from:
                    raise ValidationError(_("Date from required"))
                if contract_date_end and rec.date_to > contract_date_end:
                    raise ValidationError(
                        _("Date to Must Be Before Contract Date")
                    )
            if rec.date_from:
                if not rec.date_to:
                    raise ValidationError(_("Date To required"))
                if rec.date_from > rec.date_to:
                    raise ValidationError(
                        _("Date from Must be after Date to"))
                if rec.date_from < rec.contract_id.date_start:
                    raise ValidationError(
                        _("Date Should Be After Contract Date")
                    )

            line = self.search([
                ('contract_id', '=', rec.contract_id.id),
                ('name', '=', rec.name.id),
                ('id', '!=', rec.id),
            ], limit=1)
            if line:
                if rec.date_from and rec.date_to and \
                        line.date_to and line.date_from:
                    if line.date_from <= rec.date_from <= line.date_to or \
                            line.date_from <= rec.date_to <= line.date_to:
                        raise ValidationError(_("Date Overlapping"))
                elif not rec.date_from and not rec.date_to and \
                        not line.date_from and not line.date_to:
                    raise ValidationError(_("Date Overlapping"))
