""" Job Level """

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HrJobLevel(models.Model):
    """ Job Level model to define job titles and levels """
    _name = 'hr.job.level'
    _description = 'Job Level'
    _sql_constraints = [
        ('unique_name', 'UNIQUE(name,company_id)', 'Name must be unique'),
        ('unique_level', 'UNIQUE(level,company_id)', 'Level must be unique')
    ]

    name = fields.Char(
        string='Title',
        required=True,
        translate=True
    )
    level = fields.Char(
        required=True,
        translate=True
    )
    code = fields.Integer()
    schema = fields.Selection(
        [('top', 'Top Management'),
         ('mid', 'Mid Management'),
         ('staff', 'Staff')],
        required=True
    )
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company.id
    )

    @api.constrains('code', 'company_id')
    def _check_levels(self):
        """
            check company levelling configuration to ensure levels wont exceed
        """
        levels = len(self.search([
            '|', ('company_id', '=', self.env.company.id),
            ('company_id', '=', False)
        ]))
        org_level_config = self.env.company.organization_levelling
        if levels > org_level_config:
            raise ValidationError(
                _('%(company_name)s levelling cannot '
                  'exceed %(org_level_config)s levels') % {
                      "company_name": self.env.company.name,
                      "org_level_config": org_level_config
                  }
            )
